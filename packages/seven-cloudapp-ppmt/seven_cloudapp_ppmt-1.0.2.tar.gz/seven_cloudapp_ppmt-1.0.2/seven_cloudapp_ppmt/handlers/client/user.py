# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-05-19 11:33:16
:LastEditTime: 2021-02-24 15:58:07
:LastEditors: HuangJingCan
:description: 用户处理
"""
from seven_cloudapp.handlers.top_base import *
from seven_cloudapp.libs.customize.seven import *

from seven_cloudapp.models.behavior_model import *
from seven_cloudapp.models.seven_model import PageInfo

from seven_cloudapp.models.db_models.user.user_info_model import *
from seven_cloudapp.models.db_models.app.app_info_model import *
from seven_cloudapp.models.db_models.pay.pay_order_model import *
from seven_cloudapp.models.db_models.prize.prize_order_model import *
from seven_cloudapp.models.db_models.coin.coin_order_model import *
from seven_cloudapp.models.db_models.price.price_gear_model import *
from seven_cloudapp.models.db_models.gear.gear_value_model import *
from seven_cloudapp.models.db_models.ip.ip_series_model import *

from seven_cloudapp.handlers.client.user import UserHandler
from seven_cloudapp.handlers.client.user import LoginHandler

from seven_cloudapp_ppmt.models.db_models.act.act_info_model import *
from seven_cloudapp_ppmt.models.db_models.act.act_prize_model import *
from seven_cloudapp_ppmt.models.db_models.machine.machine_info_model import *
from seven_cloudapp_ppmt.models.db_models.prize.prize_roster_model import *


class SyncPayOrderHandler(TopBaseHandler):
    """
    :description: 用户支付订单提交
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 用户支付订单提交
        :param act_id:活动id
        :return dict
        :last_editors: HuangJianYi
        """
        act_id = self.get_param("act_id")
        open_id = self.get_taobao_param().open_id
        app_id = self.get_taobao_param().source_app_id

        access_token = ""
        app_info = AppInfoModel().get_entity("app_id=%s", params=app_id)
        if app_info:
            access_token = app_info.access_token
        user_info_model = UserInfoModel()
        user_info = user_info_model.get_entity("act_id=%s and open_id=%s", params=[act_id, open_id])
        if not user_info:
            return self.reponse_json_error('NoUser', '对不起，用户不存在')
        act_info_model = ActInfoModel()
        act_info = act_info_model.get_entity('id=%s', params=[act_id])
        if not act_info:
            return self.reponse_json_error('NoAct', '对不起，活动不存在')

        # 获取订单
        order_data = self.get_taobao_order(open_id, access_token)
        # self.logger_info.info(str(order_data) + "【订单列表】")

        #获取所有盲盒配置
        machine_info_model = MachineInfoModel()
        machine_config_list = machine_info_model.get_list("act_id=%s", params=[act_id])

        #获取价格档位配置
        price_gear_model = PriceGearModel()
        price_gear_list = price_gear_model.get_list("act_id=%s", params=[act_id])

        pay_order_model = PayOrderModel()
        pay_order_list = pay_order_model.get_list("open_id=%s and act_id=%s", order_by="id desc", params=[open_id, act_id])

        pay_order_id_list = []
        for item in pay_order_list:
            pay_order_id_list.append(item.order_no)

        buy_goods_id_list = []
        for item in price_gear_list:
            buy_goods_id_list.append(item.goods_id)

        #所有订单(排除交易结束订单)
        all_sub_order_list = []
        #所有相关商品订单
        all_goods_order_list = []

        #过滤掉不奖励的数据和跟活动无关的订单
        if order_data:
            for item in order_data:
                for order in item["orders"]["order"]:
                    if str(order["num_iid"]) in buy_goods_id_list:
                        if order["status"] in self.rewards_status():
                            order["pay_time"] = item["pay_time"]
                            order["tid"] = item["tid"]
                            all_sub_order_list.append(order)
                        if "pay_time" in item:
                            order["tid"] = item["tid"]
                            order["pay_time"] = item["pay_time"]
                            all_goods_order_list.append(order)

        add_lottery_count = False
        total_pay_num = 0
        total_pay_prize = 0
        total_pay_order_num = 0
        user_info_dict = {}
        try:

            for order in all_sub_order_list:
                #判断是否已经加过奖励
                if order["oid"] not in pay_order_id_list:

                    pay_order = PayOrder()
                    pay_order.app_id = app_id
                    pay_order.act_id = act_id
                    pay_order.open_id = open_id
                    pay_order.owner_open_id = act_info.owner_open_id
                    pay_order.user_nick = user_info.user_nick
                    pay_order.main_order_no = order['tid']
                    pay_order.order_no = order['oid']
                    pay_order.goods_code = order['num_iid']
                    pay_order.goods_name = order['title']
                    pay_order.sku_id = order['sku_id']
                    pay_order.buy_num = order['num']
                    pay_order.pay_price = order['payment']
                    pay_order.order_status = order['status']
                    pay_order.create_date = self.get_now_datetime()
                    pay_order.pay_date = order['pay_time']

                    now_price_gear_config = {}
                    for price_config in price_gear_list:
                        if (price_config.effective_date == '1900-01-01 00:00:00' or TimeHelper.format_time_to_datetime(price_config.effective_date) < TimeHelper.format_time_to_datetime(order["pay_time"])) and price_config.goods_id == str(order["num_iid"]) and price_config.sku_id == str(order["sku_id"]):
                            now_price_gear_config = price_config
                            continue

                    if now_price_gear_config:
                        if "sku_id" in order.keys():
                            pay_order.sku_name = self.get_sku_name(int(order['num_iid']), int(order['sku_id']), access_token)
                        pay_order_id = pay_order_model.add_entity(pay_order)
                        #获得次数
                        prize_count = int(order["num"])

                        gear_value_model = GearValueModel()
                        gear_value = gear_value_model.get_entity("act_id=%s and price_gears_id=%s and open_id=%s", params=[act_id, now_price_gear_config.id, open_id])
                        if not gear_value:
                            gear_value = GearValue()
                            gear_value.act_id = act_id
                            gear_value.app_id = app_id
                            gear_value.open_id = open_id
                            gear_value.price_gears_id = now_price_gear_config.id
                            gear_value.current_value = prize_count
                            gear_value.create_date = self.get_now_datetime()
                            gear_value.modify_date = self.get_now_datetime()
                            gear_value_model.add_entity(gear_value)
                        else:
                            gear_value.current_value += prize_count
                            gear_value.modify_date = self.get_now_datetime()
                            gear_value_model.update_entity(gear_value)

                        user_info.pay_num += prize_count
                        user_info.pay_price = str(decimal.Decimal(user_info.pay_price) + decimal.Decimal(order["payment"]))
                        user_info_model.update_entity(user_info)

                        gear_value_list_dict = gear_value_model.get_dict_list("act_id=%s and open_id=%s", params=[act_id, open_id])

                        total_pay_num += 1
                        total_pay_prize = str(decimal.Decimal(total_pay_prize) + decimal.Decimal(order["payment"]))
                        total_pay_order_num += int(order["num"])
                        add_lottery_count = True
                        user_info_dict = user_info.__dict__
                        user_info_dict["machine_value_list"] = gear_value_list_dict

                        #添加记录
                        coin_order_model = CoinOrderModel()
                        coin_order = CoinOrder()
                        coin_order.open_id = open_id
                        coin_order.app_id = app_id
                        coin_order.act_id = act_id
                        coin_order.price_gears_id = now_price_gear_config.id
                        coin_order.reward_type = 0
                        coin_order.goods_name = pay_order.goods_name
                        coin_order.goods_price = pay_order.pay_price
                        coin_order.sku = pay_order.sku_id
                        coin_order.nick_name = pay_order.user_nick
                        coin_order.main_pay_order_no = pay_order.main_order_no
                        coin_order.pay_order_no = pay_order.order_no
                        coin_order.pay_order_id = pay_order_id
                        coin_order.buy_count = prize_count
                        coin_order.surplus_count = prize_count
                        coin_order.pay_date = pay_order.pay_date
                        coin_order.create_date = self.get_now_datetime()
                        coin_order.modify_date = self.get_now_datetime()
                        coin_order_model.add_entity(coin_order)
                    #结束

        except Exception as ex:
            self.logger_info.info(str(all_sub_order_list) + "【订单列表】" + str(ex))
            return self.reponse_json_error('Error', '获取订单失败')

        if user_info.user_state == 0 and act_info.is_black == 1 and act_info.refund_count > 0:
            #退款的订单  子订单存在退款 记录一次
            # refund_order_data = [i for i in all_goods_order_list if [j for j in i if j["refund_status"] not in self.refund_status()]]
            refund_order_data = [i for i in all_goods_order_list if i["refund_status"] not in self.refund_status()]
            #如果不是黑用户 并且存在退款时间 代表黑用户解禁
            if user_info.relieve_date != '1900-01-01 00:00:00':
                refund_order_data = [i for i in refund_order_data if TimeHelper.format_time_to_datetime(i['pay_time']) > TimeHelper.format_time_to_datetime(user_info.relieve_date)]
            #超过变成黑用户
            if len(refund_order_data) >= act_info.refund_count:
                user_info_model.update_table("user_state=1", "id=%s", user_info.id)
                user_info_dict["user_state"] = 1

        result = {}
        if add_lottery_count == True:
            result["user_info"] = user_info_dict
            result["total_pay_order_num"] = total_pay_order_num
            result["total_pay_num"] = total_pay_num
            result["total_pay_prize"] = total_pay_prize

            behavior_model = BehaviorModel()
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_info.owner_open_id, 'PayMoneyCount', decimal.Decimal(total_pay_prize))
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_info.owner_open_id, 'PayerCount', 1)
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_info.owner_open_id, 'PayCount', total_pay_num)

            self.reponse_json_success(result)
        else:
            self.reponse_json_success()


class PrizeOrderHandler(SevenBaseHandler):
    """
    :description: 用户订单列表
    """
    def get_async(self):
        """
        :description: 用户订单列表
        :param act_id：活动id
        :param page_index：页索引
        :param page_size：页大小
        :return list
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        open_id = self.get_taobao_param().open_id

        act_id = int(self.get_param("act_id", 0))
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 20))

        prize_order_model = PrizeOrderModel()
        prize_roster_model = PrizeRosterModel()
        ip_series_model = IpSeriesModel()
        prize_order_list_dict, total = prize_order_model.get_dict_page_list("*", page_index, page_size, "open_id=%s and act_id=%s", "", "create_date desc", [open_id, act_id])
        if prize_order_list_dict:
            prize_order_id_list = [str(i["id"]) for i in prize_order_list_dict]
            prize_order_ids = ",".join(prize_order_id_list)
            prize_roster_list_dict = prize_roster_model.get_dict_list("prize_order_id in (" + prize_order_ids + ")")

            ip_series_list_dict = []
            ip_series_id_list = [str(i["series_id"]) for i in prize_roster_list_dict]
            if len(ip_series_id_list) > 0:
                ip_series_id_ids = ",".join(ip_series_id_list)
                ip_series_list_dict = ip_series_model.get_dict_list("id in (" + ip_series_id_ids + ")")

            for i in range(len(prize_order_list_dict)):
                prize_list = [prize_roster for prize_roster in prize_roster_list_dict if prize_order_list_dict[i]["id"] == prize_roster["prize_order_id"]]
                cur_prize = prize_list[0] if len(prize_list) > 0 else None
                cur_series_id = cur_prize["series_id"] if cur_prize != None else 0
                series_name_list = [ip_series["series_name"] for ip_series in ip_series_list_dict if cur_series_id == ip_series["id"]]
                prize_order_list_dict[i]["series_name"] = series_name_list[0] if len(series_name_list) > 0 else ""
                prize_order_list_dict[i]["prize_list"] = prize_list

        page_info = PageInfo(page_index, page_size, total, prize_order_list_dict)

        self.reponse_json_success(page_info)


class GetNumByPriceGearsListHandler(SevenBaseHandler):
    """
    :description: 获取价格档位对应的抽盒次数
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取价格档位对应的抽盒次数
        :param act_id：活动id
        :param page_index：页索引
        :param page_size：页大小
        :return: list
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        open_id = self.get_taobao_param().open_id
        act_id = int(self.get_param("act_id", 0))

        price_gear_model = PriceGearModel()
        ip_series_model = IpSeriesModel()
        gear_value_model = GearValueModel()
        machine_info_model = MachineInfoModel()
        result_price_gear_list = []
        price_gear_list = price_gear_model.get_dict_list("act_id=%s and is_del=0", params=[act_id])
        if len(price_gear_list) > 0:
            id_list = [price_gear["id"] for price_gear in price_gear_list]
            id_ids = ','.join("'" + str(i) + "'" for i in id_list)

            #获取有绑定机台的价格档位
            machine_info_list = machine_info_model.get_dict_list(f"act_id='{act_id}' and is_release=1 and price_gears_id in ({id_ids})", "price_gears_id", "", "", "price_gears_id,count(price_gears_id) as num")
            #用户档位次数列表
            gear_value_list = gear_value_model.get_dict_list(f"act_id='{act_id}' and open_id='{open_id}' and price_gears_id in ({id_ids})")
            for price_gear in price_gear_list:
                machine_info_filter = [machine_info for machine_info in machine_info_list if machine_info["price_gears_id"] == price_gear["id"]]
                if len(machine_info_filter) <= 0:
                    continue
                gear_value_list_filter = [gear_value for gear_value in gear_value_list if gear_value["price_gears_id"] == price_gear["id"]]
                if len(gear_value_list_filter) <= 0:
                    price_gear["gear_value"] = 0
                else:
                    price_gear["gear_value"] = gear_value_list_filter[0]["current_value"]
                result_price_gear_list.append(price_gear)

        self.reponse_json_success(result_price_gear_list)


class GetUnpackNumHandler(SevenBaseHandler):
    """
    :description: 获取拆盒次数
    """
    def get_async(self):
        """
        :description: 获取拆盒次数
        :param machine_id:机台id
        :param act_id:活动id
        :return dict
        :last_editors: HuangJianYi
        """
        open_id = self.get_taobao_param().open_id
        machine_id = int(self.get_param("machine_id", 0))
        act_id = int(self.get_param("act_id", 0))

        gear_value_model = GearValueModel()
        price_gear_model = PriceGearModel()
        machine_info_model = MachineInfoModel()
        result_info = {}
        result_info["gear_value"] = 0
        machine_info = machine_info_model.get_entity("id=%s and is_release=1", params=[machine_id])
        if machine_info:
            if machine_info.price_gears_id > 0:
                price_gear = price_gear_model.get_entity_by_id(machine_info.price_gears_id)
                if price_gear:
                    result_info["goods_id"] = price_gear.goods_id
                    result_info["sku_id"] = price_gear.sku_id
                    result_info["price_gears_id"] = price_gear.id
                    #用户档位次数
                    gear_value = gear_value_model.get_entity(f"act_id='{act_id}' and open_id='{open_id}' and price_gears_id={price_gear.id} ")
                    if gear_value:
                        result_info["gear_value"] = int(gear_value.current_value)

        self.reponse_json_success(result_info)


class PrizeOrderBySeriesHandler(SevenBaseHandler):
    """
    :description: 通过IP系列id获取用户订单列表
    """
    @filter_check_params("act_id,series_id")
    def get_async(self):
        """
        :description: 通过IP系列id获取用户订单列表
        :param act_id:活动id
        :param series_id:系列id
        :param page_index：页索引
        :param page_size：页大小
        :return list
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        open_id = self.get_taobao_param().open_id
        act_id = int(self.get_param("act_id", 0))
        series_id = int(self.get_param("series_id", 0))
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 20))

        prize_order_model = PrizeOrderModel()
        prize_roster_model = PrizeRosterModel()
        ip_series_model = IpSeriesModel()
        prize_roster_list_dict, total = prize_roster_model.get_dict_page_list("*", page_index, page_size, "open_id=%s and act_id=%s and series_id=%s", "", "create_date desc", [open_id, act_id, series_id])
        prize_order_list_dict = []
        if prize_roster_list_dict:
            prize_order_id_list = [str(i["prize_order_id"]) for i in prize_roster_list_dict]
            prize_order_ids = ",".join(prize_order_id_list)
            prize_order_list_dict = prize_order_model.get_dict_list("id in (" + prize_order_ids + ")")

            ip_series_list_dict = []
            ip_series_id_list = [str(i["series_id"]) for i in prize_roster_list_dict]
            if len(ip_series_id_list) > 0:
                ip_series_id_ids = ",".join(ip_series_id_list)
                ip_series_list_dict = ip_series_model.get_dict_list("id in (" + ip_series_id_ids + ")")
            for i in range(len(prize_order_list_dict)):
                prize_list = [prize_roster for prize_roster in prize_roster_list_dict if prize_order_list_dict[i]["id"] == prize_roster["prize_order_id"]]
                cur_prize = prize_list[0] if len(prize_list) > 0 else None
                cur_series_id = cur_prize["series_id"] if cur_prize != None else 0
                series_name_list = [ip_series["series_name"] for ip_series in ip_series_list_dict if cur_series_id == ip_series["id"]]
                prize_order_list_dict[i]["series_name"] = series_name_list[0] if len(series_name_list) > 0 else ""
                prize_order_list_dict[i]["prize_list"] = prize_list

        page_info = PageInfo(page_index, page_size, total, prize_order_list_dict)

        self.reponse_json_success(page_info)


class GetHorseRaceLampListHandler(SevenBaseHandler):
    """
    :description: 获取跑马灯奖品列表
    """
    def get_async(self):
        """
        :description: 获取跑马灯奖品列表
        :param act_id:活动id
        :param machine_id:机台id
        :param page_index：页索引
        :param page_size：页大小
        :return list
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        open_id = self.get_taobao_param().open_id
        machine_id = int(self.get_param("machine_id", 0))
        act_id = int(self.get_param("act_id", 0))
        page_size = int(self.get_param("page_size", 30))

        if machine_id == 0:
            condition = "act_id=%s"
            params = [act_id]
        else:
            condition = "act_id=%s and machine_id=%s"
            params = [act_id, machine_id]
        act_prize_list_dict = ActPrizeModel().get_dict_list("act_id=%s and is_prize_notice=0", params=[act_id])
        if act_prize_list_dict:
            prize_id_list = [str(i["id"]) for i in act_prize_list_dict]
            if len(prize_id_list) > 0:
                prize_ids = ",".join(prize_id_list)
                condition += " and prize_id not in (" + prize_ids + ")"
        condition += f" and create_date>'{TimeHelper.add_hours_by_format_time(hour=7)}'"
        prize_roster_model = PrizeRosterModel()
        page_list = prize_roster_model.get_dict_list(condition, "", "create_date desc", str(page_size), "user_nick,prize_name,tag_id,machine_name", params)
        total = int(len(page_list))
        if total == 0:
            page_list = []
        else:
            for i in range(len(page_list)):
                if page_list[i]["user_nick"]:
                    length = len(page_list[i]["user_nick"])
                    if length > 2:
                        user_nick = page_list[i]["user_nick"][0:length - 2] + "**"
                    else:
                        user_nick = page_list[i]["user_nick"][0:1] + "*"
                    page_list[i]["user_nick"] = user_nick
        if total < page_size:
            machine_condition = "act_id=%s and is_false_prize=1"
            machine_params = [act_id]
            if machine_id > 0:
                machine_condition += " and id=%s"
                machine_params = [act_id, machine_id]
            machine_info_list = MachineInfoModel().get_list(machine_condition, params=machine_params)
            if len(machine_info_list) > 0:
                machine_id_list = [str(i.id) for i in machine_info_list]
                machine_ids = ",".join(machine_id_list)
                addNum = page_size - total
                if machine_id > 0:
                    false_act_prize_list = ActPrizeModel().get_list("act_id=%s and machine_id=%s and is_prize_notice=1", order_by="probability desc", limit="30", params=[act_id, machine_id])
                else:
                    false_act_prize_list = ActPrizeModel().get_list("act_id=%s and machine_id in (" + machine_ids + ") and is_prize_notice=1", order_by="probability desc", limit="30", params=[act_id])
                if len(false_act_prize_list) > 0:
                    user_info_list_dict = UserInfoModel().get_dict_list("app_id!=%s and open_id!=%s and user_nick!=''", order_by="RAND()", params=[app_id, open_id], limit=str(addNum))
                    random_Prize_dict_list = {}
                    for act_prize in false_act_prize_list:
                        random_Prize_dict_list[act_prize.id] = act_prize.probability

                    for i in range(len(user_info_list_dict)):
                        prize_id = self.random_weight(random_Prize_dict_list)
                        false_act_prize = [j for j in false_act_prize_list if j.id == prize_id]
                        if len(false_act_prize) <= 0:
                            continue
                        prize_roster = {}
                        if user_info_list_dict[i]["user_nick"]:
                            length = len(user_info_list_dict[i]["user_nick"])
                            if length > 2:
                                user_nick = user_info_list_dict[i]["user_nick"][0:length - 2] + "**"
                            else:
                                user_nick = user_info_list_dict[i]["user_nick"][0:1] + "*"
                        prize_roster["user_nick"] = user_nick
                        prize_roster["prize_name"] = false_act_prize[0].prize_name
                        prize_roster["tag_id"] = false_act_prize[0].tag_id
                        machine_info_filter = [machine_info for machine_info in machine_info_list if false_act_prize[0].machine_id == machine_info.id]
                        prize_roster["machine_name"] = machine_info_filter[0].machine_name if len(machine_info_filter) > 0 else ""
                        page_list.append(prize_roster)

        self.reponse_json_success(page_list)
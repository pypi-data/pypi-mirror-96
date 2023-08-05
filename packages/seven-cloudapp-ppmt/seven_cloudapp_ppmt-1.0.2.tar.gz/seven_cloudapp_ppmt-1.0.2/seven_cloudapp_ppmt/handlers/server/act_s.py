# -*- coding: utf-8 -*-
"""
:Author: CaiYouBin
:Date: 2020-05-12 20:04:54
:LastEditTime: 2021-02-24 15:58:45
:LastEditors: HuangJingCan
:description: 基础接口
"""
import random
from copy import deepcopy
from seven_cloudapp.handlers.top_base import *

from seven_cloudapp.models.db_models.app.app_info_model import *
from seven_cloudapp.models.db_models.base.base_info_model import *
from seven_cloudapp.models.db_models.behavior.behavior_orm_model import *
from seven_cloudapp.models.db_models.theme.theme_info_model import *
from seven_cloudapp.models.db_models.skin.skin_info_model import *
from seven_cloudapp.models.db_models.act.act_type_model import *
from seven_cloudapp.models.db_models.ip.ip_series_model import *
from seven_cloudapp.models.seven_model import PageInfo
from seven_cloudapp.models.behavior_model import *
from seven_cloudapp.models.enum import *

from seven_cloudapp.handlers.server.act_s import ActTypeListHandler
from seven_cloudapp.handlers.server.act_s import ActDelHandler
from seven_cloudapp.handlers.server.act_s import ActQrCodeHandler
from seven_cloudapp.handlers.server.act_s import ActReviewHandler
from seven_cloudapp.handlers.server.act_s import NextProgressHandler

from seven_cloudapp_ppmt.models.db_models.machine.machine_info_model import *
from seven_cloudapp_ppmt.models.db_models.act.act_prize_model import *
from seven_cloudapp_ppmt.models.db_models.act.act_info_model import *


class ActCreateHandler(TopBaseHandler):
    """
    :description: 创建活动
    """
    @filter_check_params("act_type")
    def get_async(self):
        """
        :Description: 创建活动
        :param act_type：活动类型
        :return: 
        :last_editors: CaiYouBin
        """
        user_nick = self.get_taobao_param().user_nick
        if not user_nick:
            return self.reponse_json_error("Error", "对不起，请先授权登录")
        open_id = self.get_taobao_param().open_id
        act_name = self.get_param("act_name")

        #实例化
        description = "购买拆盲盒次数后，直接在线拆盲盒，提前获得盲盒内的惊喜奖品！"
        icon = "https://isv.alibabausercontent.com/00000000/imgextra/i3/2206353354303/O1CN01yHzXm11heouQpXsGT_!!2206353354303-2-isvtu-00000000.png"
        name_ending = "在线抽盒机"
        app_info = self.instantiate(user_nick, act_name, description, icon, name_ending)

        #查询appInfo表后等到
        if not hasattr(app_info, 'app_id'):
            return self.reponse_json_error("Error", "对不起，实例化失败请重试")
        app_id = app_info.app_id
        act_id = self.get_param("act_id")
        act_type = self.get_param("act_type")
        act_model = ActInfoModel()
        machine_info_model = MachineInfoModel()
        theme_info_model = ThemeInfoModel()
        skin_info_model = SkinInfoModel()
        ip_series_model = IpSeriesModel()
        theme_info = theme_info_model.get_entity()
        if not theme_info:
            return self.reponse_json_error("NoTheme", "请管理员先上传主题信息")
        skin_info = skin_info_model.get_entity("theme_id=%s", params=theme_info.id)
        if not skin_info:
            return self.reponse_json_error("NoSkin", "请管理员先上传皮肤信息")

        if not act_id:
            #增加默认活动
            act_info = ActInfo()
            act_info.app_id = app_id
            #商家OpenID 查询appInfo表后得到
            act_info.owner_open_id = app_info.owner_open_id
            act_info.act_name = act_name
            act_info.act_type = act_type
            act_info.sort_index = 1
            #默认主题ID 查询theme表得到
            act_info.theme_id = theme_info.id
            act_info.store_url = ""
            act_info.close_word = "抱歉，程序维护中"
            act_info.share_desc = {"taoword": "", "icon": [{"url": "https://isv.alibabausercontent.com/010230116422/imgextra/i3/2206353354303/O1CN01BszcR21heosrbagum_!!2206353354303-2-isvtu-010230116422.png"}], "title": "", "desc": ""}
            act_info.share_desc = self.json_dumps(act_info.share_desc)
            act_info.rule_desc = [{
                "ruleName": "什么是盲盒",
                "ruleDetail": "这是一个拼RP（人品）的游戏，是一种娱乐性的人气购物体验，每个盲盒里含有不同数量商品，商品的价值远远大于盲盒的售价，但是具体出哪几个商品是随机的，可能会抽到意料之外的惊喜哦！ "
            }, {
                "ruleName": "特别说明",
                "ruleDetail": "1、本产品为在线体验商品，用户购买盲盒机次数完成在线拆盲盒（即明确盲盒内具体商品）后，即为消费完成，仓库根据用户抽取的确认款直接发货。\n" + "2、在线打开盲盒明确具体款式后，不接受任何理由退换货\n" + "3、若出现产品质量问题等。本单品一样享受售后换货流程\n" + "4、在一次抽奖中，该盲盒中不会抽到重复的商品【多次抽有可能重复】【重复指的是完全一样的商品】\n" + "5、由于盲盒的特殊性，不参加店内其他活动\n" + "6、盲盒会不定期更新，具体以该盲盒商品池中显示的商品为准\n" + "7、如果您愿意拍下，就是认同我们的活动规则，介意者也不勉强，可以自由选择关闭页面或者浏览我们的其他商品\n" + "8、本活动最终解释权归XXXX所有\n"
            }]
            act_info.rule_desc = self.json_dumps(act_info.rule_desc)
            act_info.start_date = "2020-02-25 00:00:00"
            act_info.end_date = "2100-02-25 00:00:00"
            act_info.is_black = 0
            act_info.is_release = 1
            act_info.index_desc = {"index_pic_istemplate": 0, "index_pic": [{"url": "https://isv.alibabausercontent.com/010230116422/imgextra/i4/2206353354303/O1CN0164WKym1heosiC9by5_!!2206353354303-2-isvtu-010230116422.png"}], "index_notice": "选一个喜欢的系列试试吧~抽盒次数购买后概不退款~"}
            act_info.index_desc = self.json_dumps(act_info.index_desc)
            act_info.shakebox_tips = ["根据客官多年的摇盒经验，里面一定不会是XX。", "客官手法如此专业，是祖传的吧！", "摇一摇，摇到外婆桥~"]
            act_info.shakebox_tips = self.json_dumps(act_info.shakebox_tips)
            act_info.shakebox_tips_num = 3
            act_info.exceed_tips = "再摇玩具就损坏啦~"
            act_info.create_date = self.get_now_datetime()
            act_info.modify_date = self.get_now_datetime()
            act_id = act_model.add_entity(act_info)

            #添加默认IP系列
            ip_series = IpSeries()
            ip_series.act_id = act_id
            ip_series.app_id = app_id
            ip_series.series_name = "测试系列"
            ip_series.series_pic = "https://isv.alibabausercontent.com/010230116422/imgextra/i4/2206353354303/O1CN01lRxBzW1heosy7EBjJ_!!2206353354303-2-isvtu-010230116422.png"
            ip_series.sort_index = 0
            ip_series.is_release = 1
            ip_series.modify_date = self.get_now_datetime()
            ip_series.create_date = ip_series.modify_date
            ip_seriesid = ip_series_model.add_entity(ip_series)
            #增加默认机台.
            machine_info = MachineInfo()
            machine_info.machine_name = "测试数据"
            machine_info.machine_type = 2
            machine_info.act_id = act_id
            machine_info.app_id = app_id
            machine_info.machine_price = 0
            #SKUid待定
            machine_info.sku_id = 0
            machine_info.skin_id = skin_info.id
            machine_info.sort_index = 1
            machine_info.is_release = 1
            machine_info.single_lottery_price = 0
            machine_info.many_lottery_price = 0
            machine_info.many_lottery_num = 0
            machine_info.is_false_prize = 1
            machine_info.is_repeat_prize = 1
            machine_info.price_gears_id = 0
            machine_info.series_id = ip_seriesid
            machine_info.specs_type = 6
            machine_info.index_pic = "https://isv.alibabausercontent.com/010230116422/imgextra/i4/2206353354303/O1CN01lRxBzW1heosy7EBjJ_!!2206353354303-2-isvtu-010230116422.png"
            machine_info.goods_detail = []
            machine_info.goods_detail = self.json_dumps(machine_info.goods_detail)
            machine_info.box_style_type = 1
            machine_info.box_style_detail = {}
            machine_info.box_style_detail = self.json_dumps(machine_info.box_style_detail)
            machine_info.sale_type = 1
            machine_info.sale_date = "1900-01-01 00:00:00"
            machine_info.create_date = self.get_now_datetime()
            machine_info.modify_date = self.get_now_datetime()
            machine_infoid = machine_info_model.add_entity(machine_info)

            #增加行为映射数据
            orm_infos = []
            for i in range(0, 2):
                behavior_orm = BehaviorOrm()
                if i == 0:
                    behavior_orm.is_repeat = 0
                    behavior_orm.key_value = machine_info.machine_name + "拆开次数"
                    behavior_orm.key_name = "openCount_" + str(machine_infoid)
                else:
                    behavior_orm.is_repeat = 1
                    behavior_orm.repeat_type = 1
                    behavior_orm.key_value = machine_info.machine_name + "拆开人数"
                    behavior_orm.key_name = "openUserCount_" + str(machine_infoid)
                behavior_orm.orm_type = 1
                behavior_orm.group_name = ""
                behavior_orm.is_common = 0
                behavior_orm.sort_index = 1
                behavior_orm.app_id = app_id
                behavior_orm.act_id = act_id
                behavior_orm.create_date = self.get_now_datetime()
                orm_infos.append(behavior_orm)
            BehaviorModel().save_orm(orm_infos, act_id)

            self.save_default_prize(act_id, app_id, app_info.owner_open_id, machine_infoid)

            self.create_operation_log(OperationType.add.value, act_info.__str__(), "ActCreateHandler", None, self.json_dumps(act_info))

        self.reponse_json_success(act_id)

    def save_default_prize(self, act_id, app_id, owner_open_id, machine_infoid):
        act_prize_model = ActPrizeModel()
        act_prize_list = []
        for i in range(0, 2):
            act_prize = ActPrize()
            act_prize.act_id = act_id
            act_prize.app_id = app_id
            act_prize.owner_open_id = owner_open_id
            act_prize.machine_id = machine_infoid
            act_prize.prize_name = "奖品测试标题" + str(i + 1)
            act_prize.prize_title = "奖品测试子标题" + str(i + 1)
            act_prize.prize_pic = "https://isv.alibabausercontent.com/010230116422/imgextra/i4/2206353354303/O1CN01lRxBzW1heosy7EBjJ_!!2206353354303-2-isvtu-010230116422.png"
            act_prize.prize_detail = ["https://isv.alibabausercontent.com/010230116422/imgextra/i4/2206353354303/O1CN01lRxBzW1heosy7EBjJ_!!2206353354303-2-isvtu-010230116422.png"]
            # act_prize.prize_detail = self.json_dumps(act_prize.prize_detail)
            act_prize.goods_code = ""
            act_prize.prize_type = 1
            act_prize.prize_price = 88
            act_prize.probability = 50
            act_prize.surplus = 100
            act_prize.prize_limit = 0
            act_prize.prize_total = 100
            act_prize.tag_id = 1
            act_prize.hand_out = 0
            act_prize.sort_index = 1
            act_prize.is_release = 1
            act_prize.is_prize_notice = 1
            act_prize.unpack_pic = "https://isv.alibabausercontent.com/010230116422/imgextra/i2/2206353354303/O1CN014Ufky21heosxk4aCt_!!2206353354303-2-isvtu-010230116422.png"
            act_prize.toys_pic = "https://isv.alibabausercontent.com/010230116422/imgextra/i4/2206353354303/O1CN01lRxBzW1heosy7EBjJ_!!2206353354303-2-isvtu-010230116422.png"
            act_prize.create_date = self.get_now_datetime()
            act_prize.modify_date = self.get_now_datetime()
            act_prize_list.append(act_prize)
        act_prize_model.add_list(act_prize_list)


class ActHandler(SevenBaseHandler):
    """
    :description: 修改活动
    """
    @filter_check_params("act_id,act_name")
    def post_async(self):
        """
        :description: 修改活动
        :param act_id：活动id
        :param act_name：活动名称
        :param is_release：是否发布
        :param close_word：关闭小程序文案
        :param share_desc：分享配置
        :param rule_desc：规则配置
        :param is_black：是否开启退款惩罚
        :param refund_count：退款成功次数
        :param index_desc: 首页配置
        :param shakebox_tips: 摇盒提示配置
        :param shakebox_tips_num: 摇盒次数
        :param exceed_tips: 超出次数提示内容
        :return: 
        :last_editors: HuangJingCan
        """
        act_id = int(self.get_param("act_id", 0))
        act_name = self.get_param("act_name")
        is_release = int(self.get_param("is_release", 0))
        close_word = self.get_param("close_word")
        share_desc = self.get_param("share_desc", "")
        rule_desc = self.get_param("rule_desc", "")
        is_black = int(self.get_param("is_black", 0))
        refund_count = int(self.get_param("refund_count", 0))
        store_url = self.get_param("store_url")
        index_desc = self.get_param("index_desc")
        shakebox_tips = self.get_param("shakebox_tips")
        shakebox_tips_num = self.get_param("shakebox_tips_num", 0)
        exceed_tips = self.get_param("exceed_tips")

        act_info_model = ActInfoModel()
        if act_id > 0:
            # 修改活动相关信息
            act_info = act_info_model.get_entity_by_id(act_id)

            old_act_info = deepcopy(act_info)

            act_info.act_name = act_name
            act_info.is_release = is_release
            act_info.close_word = close_word
            act_info.share_desc = self.json_dumps(share_desc) if share_desc != "" else {}
            act_info.rule_desc = self.json_dumps(rule_desc) if rule_desc != "" else []
            act_info.index_desc = self.json_dumps(index_desc) if index_desc != "" else {}
            act_info.shakebox_tips = self.json_dumps(shakebox_tips) if shakebox_tips != "" else []
            act_info.shakebox_tips_num = shakebox_tips_num
            act_info.exceed_tips = exceed_tips
            act_info.is_black = is_black
            act_info.refund_count = refund_count
            act_info.store_url = store_url
            act_info.modify_date = self.get_now_datetime()

            act_info_model.update_entity(act_info)

            self.create_operation_log(OperationType.update.value, act_info.__str__(), "ActHandler", self.json_dumps(old_act_info), self.json_dumps(act_info))

        self.reponse_json_success()


class ActListHandler(SevenBaseHandler):
    """
    :description: 活动列表
    :param {type} 
    :return: 
    :last_editors: HuangJianYi
    """
    def get_async(self):
        """
        :description: 获取活动列表
        :param act_name：活动名称
        :param page_index：页索引
        :param page_size：页大小
        :return: reponse_json_success
        :last_editors: HuangJianYi
        """
        act_name = self.get_param("act_name")
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 10))
        is_del = int(self.get_param("is_del", 0))

        app_id = self.get_app_id()
        if app_id:
            order_by = "id ASC"
            condition = "app_id=%s"
            if is_del == 0:
                condition += "AND is_del=0"
            else:
                condition += "AND is_del=1"

            page_list, total = ActInfoModel().get_dict_page_list("*", page_index, page_size, condition, "", order_by, app_id)

            for page in page_list:
                page["share_desc"] = self.json_loads(page["share_desc"]) if page["share_desc"] else {}
                page["rule_desc"] = self.json_loads(page["rule_desc"]) if page["rule_desc"] else []
                page["index_desc"] = self.json_loads(page["index_desc"]) if page["index_desc"] else {}
                page["shakebox_tips"] = self.json_loads(page["shakebox_tips"]) if page["shakebox_tips"] else []
                page["menu_configed"] = self.json_loads(page["menu_configed"]) if page["menu_configed"] else []
                page["online_url"] = self.get_online_url(page['id'], app_id)
                page["live_url"] = self.get_live_url(app_id)
                page["finish_status"] = page["finish_progress"]

            page_info = PageInfo(page_index, page_size, total, page_list)

            self.reponse_json_success(page_info)
        else:
            self.reponse_json_success({"data": []})


class ActInfoHandler(SevenBaseHandler):
    """
    :description: 活动信息获取
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 活动信息获取
        :param act_id：活动id
        :return: 活动信息
        :last_editors: HuangJingCan
        """
        act_id = int(self.get_param("act_id", "0"))

        act_info = ActInfoModel().get_entity_by_id(act_id)

        if act_info:
            act_info.share_desc = self.json_loads(act_info.share_desc)
            act_info.rule_desc = self.json_loads(act_info.rule_desc)
            act_info.index_desc = self.json_loads(act_info.index_desc)
            act_info.shakebox_tips = self.json_loads(act_info.shakebox_tips)
            if act_info.menu_configed != "":
                act_info.menu_configed = self.json_loads(act_info.menu_configed)
            else:
                act_info.menu_configed = self.json_loads("[]")
            act_info.online_url = self.get_online_url(act_info.id, act_info.app_id)
            act_info.live_url = self.get_live_url(act_info.app_id)

            self.reponse_json_success(act_info)
        else:
            self.reponse_json_success()
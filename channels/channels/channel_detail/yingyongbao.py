#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import download, log_page
from channels.settings import APK_DOWNLOAD_DIR
import json

def send_yingyongbao_request(url, **kwargs):
    apk_name = kwargs['apk_name']
    return FormRequest(url,
                  formdata={'kw': apk_name,
                            'pns': '',
                            'sid': ''},
                  method='GET',
                  meta=kwargs,
                  callback=get_yingyongbao_search_list)


def get_yingyongbao_search_list(response):
    log_page(response, 'get_yingyongbao_search_list.html')
    # 应用宝是异步获取json格式的数据。
    data = json.loads(response.body)
    # 获取列表第一条数据
    """
    {"description":"招商银行手机银行3.0全新升级，闪耀登场。完美适配2K大屏安卓手机，包含68项功能更新，为您打造更加专业、简单、安全的移动互联新生活！\r\n
    时代在变，从未改变的是因您而变！\r\n
    六大特性，满足最挑剔的你：\r\n
    ★转账免费：即日起至2015年底，转账0费用，每日高达20万元的转账汇款额度；使用优KEY转账，每日额度更可高至50万元！\r\n
    ★智能金融：账户总览，轻松管理名下所有资产；理财日历，金融琐事智能提醒。\r\n
    ★生活助手：掌上商城、话费充值、商旅预订、彩票投注、电影票在线选座等，是您贴心生活的好助手！\r\n
    ★还款快捷：信用卡账单随查随还，额度实时恢复，更支持中、农、建等多家银行借记卡免手续费还款！\r\n
    ★理财专享：手机银行客户独享专属高收益理财产品。更有专属日日盈产品，满足对流动性有更高要求的您。\r\n
    ★安全无忧：秉承业界最高安全标准，除采用SSL加密通信协议确保数据全程加密，登录IP变动检测、转账额度自主设置等安全措施外、同时增加登录密码键盘加密机制、用户自定义手机银行后台在线等多种防护措施。在涉及用户资金安全的交易中，短信验证码验证用户身份，时刻保障客户资金安全。",
    "flag":16469,
    "fileSize":5424478,
    "authorId":598794,
    "categoryId":107,
    "pkgName":"cmb.pb",
    "appId":6504,
    "appName":"招商银行",
    "apkUrl":"http://dd.myapp.com/16891/FCA4290E1CE5B7A5B2ACFF83AD156BA1.apk?fsname=cmb.pb_3.1.0_310.apk&asr=8eff",
    "versionCode":310,
    "iconUrl":"http://pp.myapp.com/ma_icon/0/icon_6504_21035686_1430874297/96",
    "versionName":"3.1.0",
    "appDownCount":7291974,
    "averageRating":3.5436363636363635,
    "editorIntro":"招商银行，您的贴身金融管家",
    "categoryName":"生活",
    "images":["http://pp.myapp.com/ma_pic2/0/shot_6504_21035686_1_1430874294/550",
              "http://pp.myapp.com/ma_pic2/0/shot_6504_21035686_2_1430874294/550",
              "http://pp.myapp.com/ma_pic2/0/shot_6504_21035686_3_1430874294/550",
              "http://pp.myapp.com/ma_pic2/0/shot_6504_21035686_4_1430874294/550",
              "http://pp.myapp.com/ma_pic2/0/shot_6504_21035686_5_1430874294/550"],
    "apkMd5":"FCA4290E1CE5B7A5B2ACFF83AD156BA1",
    "authorName":"招商银行股份有限公司",
    "apkPublishTime":1430874299,
    "appRatingInfo":{"averageRating":3.5436363636363635,"ratingCount":550,"ratingDistribution":{"1":147,"2":30,"3":37,"4":49,"5":287}}}
    """
    i = data['obj']['appDetails'][0]
    app_name = i['appName']

    apk_name = response.meta['apk_name']

    if app_name.encode('utf8') != apk_name:
        return None

    app_pn = i['pkgName']
    app_link = i['apkUrl']
    app_version = i['versionName']
    app_size = i['fileSize']
    # app_channel = 'yingyongbao'
    app_channel = response.meta['app_channel']
    save_dir = os.path.sep.join([APK_DOWNLOAD_DIR, apk_name])

    params_dic = {} # 参数字典
    params_dic['app_channel'] = app_channel     # 渠道
    params_dic['app_detail_url'] = response.url # apk下载页面
    params_dic['app_link'] = app_link           # apk下载链接
    params_dic['save_dir'] = save_dir           # 下载apk保存的目录
    params_dic['app_name'] = app_name           # 要下载的apk的应用名称
    params_dic['app_pn'] = app_pn               # apk包名
    params_dic['app_version'] = app_version     # apk版本号
    params_dic['app_size'] = app_size           # apk文件的大小

    return download(**params_dic)
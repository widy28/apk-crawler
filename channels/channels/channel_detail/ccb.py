#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import *
from channels.settings import APK_DOWNLOAD_DIR


def send_ccb_request(url, **kwargs):
    return FormRequest(url,
                    method='GET',
                    meta=kwargs,
                    callback=get_ccb_detail_url)


def get_ccb_detail_url(response):
    log_page(response, 'get_ccb_detail_url.html')

    html = Selector(response)
    detail_url = html.xpath('//div[@acqcolumnid="fuwuzhinan"]/div/ul[6]/li//a/@href').extract()[0]
    apk_name = u'中国建设银行手机银行Android客户端'
    m = response.meta
    m['apk_name'] = apk_name
    yield Request(detail_url, callback=get_ccb_detail, meta=m)


def get_ccb_detail(response):
    log_page(response, 'get_ccb_detail.html')
    html = Selector(response)

    # app_channel = 'ccb'
    app_channel = response.meta['app_channel']
    apk_name = response.meta['apk_name']
    app_name = apk_name

    try:
        app_link = html.xpath('//div[@class="text_tab_contents js_text_tab_contents"]/div[3]/p[10]/span/span/a/@href').extract()[0].strip()
    except:
        ## xpath有误。
        add_error_app_info(app_channel, app_name, '0')
        return None
    app_pn = ''
    app_version = ''
    app_size = ''
    save_dir = os.path.sep.join([APK_DOWNLOAD_DIR, apk_name])
    app_download_times = ''


    params_dic = {} # 参数字典
    params_dic['app_channel'] = app_channel     # 渠道
    params_dic['app_detail_url'] = response.url # apk下载页面
    params_dic['app_download_times'] = app_download_times  # apk下载次数
    params_dic['app_link'] = app_link           # apk下载链接
    params_dic['save_dir'] = save_dir           # 下载apk保存的目录
    params_dic['app_name'] = app_name           # 要下载的apk的应用名称
    params_dic['app_pn'] = app_pn               # apk包名
    params_dic['app_version'] = app_version     # apk版本号
    params_dic['app_size'] = app_size           # apk文件的大小

    return download(**params_dic)
#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import *
from channels.settings import APK_DOWNLOAD_DIR


def send_bankofchina_request(url, **kwargs):
    apk_name = u'中国银行Android客户端'
    kwargs['apk_name'] = apk_name
    return FormRequest(url,
                    method='GET',
                    meta=kwargs,
                    callback=get_bankofchina_download_detail)

def get_bankofchina_download_detail(response):
    log_page(response, 'get_bankofchina_download_detail.html')
    html = Selector(response)

    try:
        detail_url = 'http://www.bankofchina.com/ebanking' + html.xpath('//*[@id="wrapper"]/div[4]/div[3]/ul/li[1]/a/@href').extract()[0].replace('..', '')
    except:
        ## xpath有误。
        add_error_app_info(response.meta['app_channel'], response.meta['apk_name'], '0')
        yield None
    yield Request(detail_url, callback=get_bankofchina_detail, meta=response.meta)

def get_bankofchina_detail(response):
    log_page(response, 'get_bankofchina_detail.html')
    html = Selector(response)

    # app_channel = 'bankofchina'
    app_channel = response.meta['app_channel']
    apk_name = response.meta['apk_name']
    app_name = apk_name

    try:
        app_link = html.xpath('//table[1]/tbody/tr[1]/td[2]/a[1]/@href').extract()[0].strip()
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
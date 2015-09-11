#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import *
from channels.settings import APK_DOWNLOAD_DIR

def send_hao123_request(url, **kwargs):
    apk_name = kwargs['apk_name']
    return FormRequest(url,
                  formdata={'word': apk_name},
                  method='GET',
                  meta=kwargs,
                  callback=get_hao123_search_list)


def get_hao123_search_list(response):
    log_page(response, 'get_hao123_search_list.html')

    url_list_xpath = '//div[@class="leftbox"]/ul/li/dl/dt/a/@href'
    name_list_xpath = '//div[@class="leftbox"]/ul/li/dl/dt/a/text()'
    func = get_hao123_detail
    host = 'http://mob.hao123.com'
    result = get_search_list(response, url_list_xpath, name_list_xpath, func, host)
    if type(result) == list:
        for r in result:
            yield r
    else:
        yield result


def get_hao123_detail(response):
    log_page(response, 'get_hao123_detail.html')
    html = Selector(response)

    # app_channel = 'hao123'
    app_channel = response.meta['app_channel']
    apk_name = response.meta['apk_name']
    app_name = html.xpath('//span[@class="sw-name"]/text()').extract()[0]
    try:
        app_link = html.xpath('//a[@class="btn-download-apk"]/@href').extract()[0]
        app_download_times = html.xpath('//div[@class="sw-intro-inner clearfix"]/div[2]/table/tbody/tr/td[4]/span/text()').extract()[0][1:-1].split('+')[0]
    except:
        ## xpath有误。
        add_error_app_info(app_channel, app_name, '0')
        return None

    app_pn = ''
    app_version = ''
    app_size = ''
    save_dir = os.path.sep.join([APK_DOWNLOAD_DIR, apk_name])


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
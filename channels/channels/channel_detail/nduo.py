#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import *
from channels.settings import APK_DOWNLOAD_DIR
import json
import requests
import HTMLParser

def send_nduo_request(url, **kwargs):
    return Request(url,
                  method='GET',
                  meta=kwargs,
                  callback=get_nduo_token)


def get_nduo_token(response):
    log_page(response, 'get_nduo_token.html')
    html = Selector(response)
    token = html.xpath('//input[@class="ndoo_token"]/@value').extract()[0]
    url = 'http://www.nduoa.com/search?sk=%s&q=%s'%(token, response.meta['apk_name'])
    return FormRequest(url,
                  method='GET',
                  meta=response.meta,
                  callback=get_nduo_search_list)


def get_nduo_search_list(response):
    log_page(response, 'get_nduo_search_list.html')

    url_list_xpath = '//ul[@id="searchList"]/li/div[@class="name"]/a/@href'
    name_list_xpath = '//ul[@id="searchList"]/li/div[@class="name"]/a/span[@class="title"]/text()'
    func = get_nduo_detail
    host = 'http://www.nduoa.com'
    result = get_search_list(response, url_list_xpath, name_list_xpath, func, host)
    if type(result) == list:
        for r in result:
            yield r
    else:
        yield result


def get_nduo_detail(response):
    log_page(response, 'get_nduo_detail.html')
    html = Selector(response)

    # app_channel = 'nduo'
    app_channel = response.meta['app_channel']
    apk_name = response.meta['apk_name']
    app_name = apk_name
    try:
        app_link = 'http://www.nduoa.com' + html.xpath('//a[@id="BDTJDownload"]/@href').extract()[0]
        app_pn = ''
        app_version = html.xpath('//div[@class="name"]/span[@class="version"]/text()').extract()[0][1:-1]
        app_download_times = html.xpath('//div[@class="levelCount"]/span[@class="count"]/text()').extract()[0]
    except:
        ## xpath有误。
        add_error_app_info(app_channel, app_name, '0')
        return None

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
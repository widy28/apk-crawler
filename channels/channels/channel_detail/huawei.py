#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import *
from channels.settings import APK_DOWNLOAD_DIR

def send_huawei_request(url, **kwargs):
    apk_name = kwargs['apk_name']
    url = url + apk_name
    return FormRequest(url=url,
                  method='POST',
                  meta=kwargs,
                  callback=get_huawei_search_list)

def get_huawei_search_list(response):
    log_page(response, 'get_huawei_search_list.html')

    url_list_xpath = '//div[@class="game-info  whole"]/h4/a/@href'
    name_list_xpath = '//div[@class="game-info  whole"]/h4/a/@title'
    func = get_huawei_detail
    host = ''
    result = get_search_list(response, url_list_xpath, name_list_xpath, func, host)
    if type(result) == list:
        for r in result:
            yield r
    else:
        yield result

    # html = Selector(response)
    # search_url_list = html.xpath('//div[@class="game-info  whole"]/h4/a/@href').extract()
    # search_name_list = html.xpath('//div[@class="game-info  whole"]/h4/a/@title').extract()
    # apk_name = response.meta['apk_name']
    # if apk_name in search_name_list:
    #     detail_url = search_url_list[search_name_list.index(apk_name)]
    #     yield Request(detail_url, meta=response.meta, callback=get_huawei_detail)
    # else:
    #     yield None

def get_huawei_detail(response):
    log_page(response, 'get_huawei_detail.html')
    html = Selector(response)

    # app_channel = 'huawei'
    app_channel = response.meta['app_channel']
    apk_name = response.meta['apk_name']
    app_name = html.xpath('//div[@class="app-function nofloat"]/a/@name').extract()[0]

    try:
        app_link = html.xpath('//div[@class="app-function nofloat"]/a/@dlurl').extract()[0]
    except:
        ## xpath有误。
        add_error_app_info(app_channel, app_name, '0')
        return None

    app_version = html.xpath('//div[@class="app-function nofloat"]/a/@version').extract()[0]
    app_pn = ''
    app_size = ''
    save_dir = os.path.sep.join([APK_DOWNLOAD_DIR, apk_name])


    params_dic = {} # 参数字典
    params_dic['app_channel'] = app_channel     # 渠道
    params_dic['app_link'] = app_link           # apk下载链接
    params_dic['save_dir'] = save_dir           # 下载apk保存的目录
    params_dic['app_name'] = app_name           # 要下载的apk的应用名称
    params_dic['app_pn'] = app_pn               # apk包名
    params_dic['app_version'] = app_version     # apk版本号
    params_dic['app_size'] = app_size           # apk文件的大小

    return download(**params_dic)




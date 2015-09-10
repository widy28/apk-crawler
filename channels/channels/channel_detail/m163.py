#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import *
from channels.settings import APK_DOWNLOAD_DIR


def send_163_request(url, **kwargs):
    apk_name = kwargs['apk_name']
    return FormRequest(url,
                    formdata={'platform': '2', 'query': apk_name},
                    method='GET',
                    meta=kwargs,
                    callback=get_163_search_list)


def get_163_search_list(response):
    log_page(response, 'get_163_search_list.html')

    url_list_xpath = '//ul[@class="list-search bg-grid-dotted"][1]/li/div/div/div[2]/h3/a/@href'
    name_list_xpath = '//ul[@class="list-search bg-grid-dotted"][1]/li/div/div/div[2]/h3/a/span/text()'
    func = get_163_detail
    host = 'http://m.163.com'
    result = get_search_list(response, url_list_xpath, name_list_xpath, func, host)
    if type(result) == list:
        for r in result:
            yield r
    else:
        yield result

    # html = Selector(response)
    # detail_url = 'http://m.163.com'+html.xpath('/html/body/div[1]/div[4]/div[1]/div[1]/div[2]/div/div/ul/li[1]/div/div/div[2]/h3/a/@href').extract()[0]
    # yield Request(detail_url, callback=get_163_detail)


def get_163_detail(response):
    log_page(response, 'get_163_detail.html')
    html = Selector(response)

    # app_channel = 'm163'
    app_channel = response.meta['app_channel']
    apk_name = response.meta['apk_name']
    try:
        app_name = html.xpath('//span[@class="f-h1"]/text()').extract()[0]
        app_link = html.xpath('//a[@class="btn-download-byandroid"]/@href').extract()[0]
    except:
        ## xpath有误。
        add_error_app_info(app_channel, apk_name, '0')
        return None

    app_pn = ''
    app_version = ''
    app_size = ''
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
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

def send_meizu_request(url, **kwargs):
    apk_name = kwargs['apk_name']
    return FormRequest(url,
                  formdata={'keyword': apk_name},
                  method='GET',
                  meta=kwargs,
                  callback=get_meizu_search_list)


def get_meizu_search_list(response):
    log_page(response, 'get_meizu_search_list.html')
    data = json.loads(response.body)
    pn = data['value']['list'][0]['package_name']
    search_name_list = [decodeHtml(l['name']) for l in data['value']['list']]
    search_pn_list = [l['package_name'] for l in data['value']['list']]

    apk_name = response.meta['apk_name']
    # print apk_name in search_name_list,'--------'
    if apk_name in search_name_list:
        pn = search_pn_list[search_name_list.index(apk_name)]
        detail_url = 'http://app.meizu.com/apps/public/detail?package_name='+pn
        yield Request(detail_url, callback=get_meizu_detail)
    else:
        yield None


def get_meizu_detail(response):
    log_page(response, 'get_meizu_detail.html')
    html = Selector(response)

    # app_channel = 'meizu'
    app_channel = response.meta['app_channle']
    apk_name = response.meta['apk_name']
    app_name = html.xpath('//*[@id="theme_content"]/div[2]/div/div[1]/h3/text()').extract()[0]
    try:
        to_download_url = 'http://app.meizu.com/apps/public/download.json?app_id=' + html.xpath('//*[@id="theme_content"]/div[1]/div[1]/div/@data-appid').extract()[0]
    except:
        ## xpath有误。
        add_error_app_info(app_channel, app_name, '0')
        return None

    app_link = get_app_link(to_download_url)
    app_pn = ''
    app_version = html.xpath('//div[@class="app_content ellipsis noPointer"]/text()').extract()[0]
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


def get_app_link(url):
    r = requests.get(url)
    data = json.loads(r.content)
    return data['value']['downloadUrl']

def decodeHtml(data):
    h = HTMLParser.HTMLParser()
    n = h.unescape(data)
    return n
#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import *
from channels.settings import APK_DOWNLOAD_DIR
import re

def send_leidian_request(url, **kwargs):
    apk_name = kwargs['apk_name']
    return FormRequest(url,
                  formdata={'q': apk_name, 'ie': 'utf-8', 'src': 'shouji_www', 't': ''},
                  method='GET',
                  meta=kwargs,
                  callback=get_leidian_search_list)


def get_leidian_search_list(response):
    log_page(response, 'get_leidian_search_list.html')

    url_list_xpath = '//ul[@class="mod-soft-list"]/li/div[@class="mod-soft-info"]/h2/a/@href'
    name_list_xpath = '//ul[@class="mod-soft-list"]/li/div[@class="mod-soft-info"]/h2/a/@title'
    func = get_leidian_detail
    host = ''
    result = get_search_list(response, url_list_xpath, name_list_xpath, func, host)
    if type(result) == list:
        for r in result:
            yield r
    else:
        yield result


def get_leidian_detail(response):
    log_page(response, 'get_leidian_detail.html')
    html = Selector(response)

    apk_name = response.meta['apk_name']

    # app_channel = 'leidian'
    app_channel = response.meta['app_channel']
    app_name = html.xpath('//*[@id="bd"]/div[2]/div[1]/div[1]/div[3]/div[1]/h1/text()').extract()[0].strip()
    app_link = get_app_link(response.body)
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


def get_app_link(content):
    p = re.compile("'downurl':(.*?),")
    res = re.search(p, content)
    data = res.group()
    url = data.split("'")[3]
    return url
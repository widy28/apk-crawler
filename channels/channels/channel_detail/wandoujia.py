#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import *
from channels.settings import APK_DOWNLOAD_DIR

def send_wandoujia_request(url, **kwargs):
    apk_name = kwargs['apk_name']
    print kwargs,'---------------'
    return FormRequest(url=url,
                  formdata={'key': apk_name},
                  method='GET',
                  meta=kwargs,
                  callback=get_wandoujia_search_list)


def get_wandoujia_search_list(response):
    log_page(response, 'get_wandoujia_search_list.html')

    url_list_xpath = '//*[@id="j-search-list"]/li[@class="card"]/div[2]/a/@href'
    name_list_xpath = '//*[@id="j-search-list"]/li[@class="card"]/div[2]/a/@title'
    func = get_wandoujia_detail
    host = ''
    result = get_search_list(response, url_list_xpath, name_list_xpath, func, host)
    if type(result) == list:
        for r in result:
            yield r
    else:
        yield result

def get_wandoujia_detail(response):
    log_page(response, 'get_wandoujia_detail.html')
    print response.meta,'0-0-00-0-0-0-0-0-0-0-0-0-0-'
    html = Selector(response)
    # app_channel = 'wandoujia'
    app_channel = response.meta['app_channel']
    apk_name = response.meta['apk_name']
    app_name = apk_name
    try:
        # app_name = html.xpath('//p[@class="app-name"]/span/text()').extract()[0]
        app_link = html.xpath('//div[@class="qr-info"]/a/@href').extract()[0]

        print app_link,'-----------------------link'
    except:
        add_error_app_info(app_channel, apk_name, '0')
        return None
    app_pn = ''
    app_version = ''
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
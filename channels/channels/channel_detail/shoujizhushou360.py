#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import *
from channels.settings import APK_DOWNLOAD_DIR

def send_360_request(url, **kwargs):
    apk_name = kwargs['apk_name']
    return FormRequest(url,
                  formdata={'kw': apk_name},
                  method='GET',
                  meta=kwargs,
                  callback=get_360_search_list)


def get_360_search_list(response):
    log_page(response, 'get_360_search_list.html')

    url_list_xpath = '//div[@class="SeaCon"]/ul/li/dl/dd/h3/a/@href'
    name_list_xpath = '//div[@class="SeaCon"]/ul/li/dl/dd/h3/a/@title'
    func = get_360_detail
    host = 'http://zhushou.360.cn'
    result = get_search_list(response, url_list_xpath, name_list_xpath, func, host)
    if type(result) == list:
        for r in result:
            yield r
    else:
        yield result

    # html = Selector(response)
    # detail_url = 'http://zhushou.360.cn' + html.xpath('//div[@class="SeaCon"]/ul/li[1]/dl/dd/h3/a/@href').extract()[0]
    # yield Request(detail_url, callback=get_360_detail)


def get_360_detail(response):
    log_page(response, 'get_360_detail.html')
    html = Selector(response)

    # app_channel = '360zhushou'
    apk_name = response.meta['apk_name']
    app_channel = response.meta['app_channel']
    app_name = html.xpath('//h2[@id="app-name"]/span/text()').extract()[0]

    try:
        app_link = html.xpath('//*[@id="app-info-panel"]/div/dl/dd/a/@href').extract()[0].split('url=')[-1]
        app_download_times = html.xpath('//*[@id="app-info-panel"]/div/dl/dd/div/span[3]/text()').extract()[0].split(u'：')[1]
    except:
        ## xpath有误。
        add_error_app_info(app_channel, app_name, '0')
        return None

    app_pn_version = app_link.split('/')[-1]
    app_pn = app_pn_version.split('_')[0]
    app_version = '.'.join(app_pn_version.split('_')[1][:-4])
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
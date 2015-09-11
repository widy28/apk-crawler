#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import *
from channels.settings import APK_DOWNLOAD_DIR
import re
import requests

"""
get_coolan_detail详情页里面的app_link 经过了2个320跳转才能得到下载地址，
组织headers和cookie都不能直接访问app_link进行下载，
只好再经过scrapy引擎处理掉302跳转请求最终获得下载链接。
将params_dic参数传递到下一步get_coolan_app_download_link。
"""

def send_coolan_request(url, **kwargs):
    apk_name = kwargs['apk_name']
    return FormRequest(url,
                    formdata={'q': apk_name},
                    method='GET',
                    meta=kwargs,
                    callback=get_coolan_search_list)


def get_coolan_search_list(response):
    log_page(response, 'get_coolan_search_list.html')

    url_list_xpath = '//*[@id="apkSearchList"]/div[@class="ex-card-body"]/ul/li[@class="media"]/div/h4/a/@href'
    name_list_xpath = '//*[@id="apkSearchList"]/div[@class="ex-card-body"]/ul/li[@class="media"]/div/h4/a/text()'
    func = get_coolan_detail
    host = 'http://www.coolapk.com'
    result = get_search_list(response, url_list_xpath, name_list_xpath, func, host)
    if type(result) == list:
        for r in result:
            yield r
    else:
        yield result

    # html = Selector(response)
    # detail_url = 'http://www.coolapk.com' + html.xpath('//*[@id="apk-4016"]/div/h4/a/@href').extract()[0]
    # yield Request(detail_url, callback=get_coolan_detail)


def get_coolan_detail(response):
    log_page(response, 'get_coolan_detail.html')
    html = Selector(response)

    # app_channel = 'coolan'
    app_channel = response.meta['app_channel']
    apk_name = response.meta['apk_name']
    app_name = html.xpath('//h1[@class="media-heading ex-apk-view-title"]/text()').extract()[0].strip().split('"')[0]

    try:
        extra = html.xpath('//a[@class="btn btn-success ex-btn-glyphicon"]/@onclick').extract()[0]
    except:
        ## xpath有误。
        add_error_app_info(app_channel, app_name, '0')
        yield None

    extra = extra[extra.find('(')+1:-2]
    app_link = ''
    app_pn = ''
    app_version = html.xpath('//h1[@class="media-heading ex-apk-view-title"]/small/text()').extract()[0]
    app_size = ''
    save_dir = os.path.sep.join([APK_DOWNLOAD_DIR, apk_name])
    app_download_times = html.xpath('//span[@class="pull-left hidden-sm hidden-xs"]/text()').extract()[0].split(u'，')[1]


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

    yield Request(get_app_link(response.body, extra),
                  meta={'params_dic': params_dic},
                  callback=get_coolan_app_download_link)


def get_coolan_app_download_link(response):
    params_dic = response.meta['params_dic']
    params_dic['app_link'] = response.url
    return download(**params_dic)



def get_app_link(content, extra):
    p = re.compile('var apkDownloadUrl = "(.*?)"')
    res = re.search(p, content)
    url = res.group().split('"')[1]
    if url:
        app_link = 'http://www.coolapk.com' + url + ('&extra='+extra if int(extra) else '')
    else:
        app_link = ''
    return app_link

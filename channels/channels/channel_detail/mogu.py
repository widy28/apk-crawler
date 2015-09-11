#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import *
from channels.settings import APK_DOWNLOAD_DIR


def send_mogu_request(url, **kwargs):
    apk_name = kwargs['apk_name']
    return FormRequest(url,
                    formdata={'keyword': apk_name},
                    method='POST',
                    meta=kwargs,
                    callback=get_mogu_search_list)


def get_mogu_search_list(response):
    log_page(response, 'get_mogu_search_list.html')

    url_list_xpath = '//div[@class="pro_box app_list app_list_b"]/ul/li/div[@class="title"]/h2/a/@href'
    name_list_xpath = '//div[@class="pro_box app_list app_list_b"]/ul/li/div[@class="title"]/h2/a/text()'
    func = get_mogu_detail
    host = 'http://www.mogustore.com/'
    result = get_search_list(response, url_list_xpath, name_list_xpath, func, host)
    if type(result) == list:
        for r in result:
            yield r
    else:
        yield result

    # html = Selector(response)
    # detail_url = 'http://www.mogustore.com/' + html.xpath('//div[@class="pro_box app_list app_list_b"]/ul/li[1]/div[@class="title"]/h2/a/@href').extract()[0]
    # yield Request(detail_url,
    #               meta=response.meta,
    #               callback=get_mogu_detail)


def get_mogu_detail(response):
    log_page(response, 'get_mogu_detail.html')
    html = Selector(response)

    # app_channel = 'mogu'
    app_channel = response.meta['app_channel']
    apk_name = response.meta['apk_name']
    app_name = apk_name
    try:
        app_link = html.xpath('//li[@class="l down"]/a/@href').extract()[0]
    except:
        ## xpath有误。
        add_error_app_info(app_channel, app_name, '0')
        return None

    app_pn = ''
    app_version = ''
    app_size = ''
    save_dir = os.path.sep.join([APK_DOWNLOAD_DIR, apk_name])
    app_download_times = html.xpath('//div[@class="sub_title"]/ul/li[6]/text()').extract()[0]


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
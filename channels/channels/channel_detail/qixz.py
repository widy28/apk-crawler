#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import *
from channels.settings import APK_DOWNLOAD_DIR


def send_7xz_request(url, **kwargs):
    apk_name = kwargs['apk_name']
    return FormRequest(url,
                    formdata={'q': apk_name},
                    method='GET',
                    meta=kwargs,
                    callback=get_7xz_search_list)


def get_7xz_search_list(response):
    log_page(response, 'get_7xz_search_list.html')

    url_list_xpath = '//ul[@class="game-index"]/li/div[1]/p[1]/a/@href'
    name_list_xpath = '//ul[@class="game-index"]/li/div[1]/p[1]/a/text()'
    func = get_7xz_detail
    host = 'http://www.7xz.com'
    result = get_search_list(response, url_list_xpath, name_list_xpath, func, host)
    if type(result) == list:
        for r in result:
            yield r
    else:
        yield result

    # html = Selector(response)
    # detail_url = 'http://apk.7xz.com' + html.xpath('//div[@class="list-page"]/ul/li[1]/p/span[1]/a/@href').extract()[0]
    # yield Request(detail_url, callback=get_7xz_detail)


def get_7xz_detail(response):
    log_page(response, 'get_7xz_detail.html')
    html = Selector(response)

    # app_channel = '7xz'
    app_channel = response.meta['app_channel']
    apk_name = response.meta['apk_name']
    app_name = apk_name

    try:
        app_link = 'http://www.7xz.com' + html.xpath('//div[@class="down"]/a[2]/@href').extract()[0]
    except:
        ## xpath有误。
        add_error_app_info(app_channel, app_name, '0')
        return None
    app_pn = ''
    app_version = ''
    app_size = ''
    save_dir = os.path.sep.join([APK_DOWNLOAD_DIR, apk_name])
    app_download_times = ''


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
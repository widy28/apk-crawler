#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import *
from channels.settings import APK_DOWNLOAD_DIR

def send_hiapk_request(url, **kwargs):
    apk_name = kwargs['apk_name']
    return FormRequest(url,
                  formdata={'key': apk_name},
                  method='GET',
                  meta=kwargs,
                  callback=get_hiapk_search_list)


def get_hiapk_search_list(response):
    log_page(response, 'get_hiapk_search_list.html')

    url_list_xpath = '//dl[@class="list_content"]/dt/span[1]/a/@href'
    name_list_xpath = '//dl[@class="list_content"]/dt/span[1]/a/text()'
    func = get_hiapk_detail
    host = 'http://apk.hiapk.com'
    result = get_search_list(response, url_list_xpath, name_list_xpath, func, host)
    if type(result) == list:
        for r in result:
            yield r
    else:
        yield result


def get_hiapk_detail(response):
    log_page(response, 'get_hiapk_detail.html')
    html = Selector(response)

    # app_channel = 'hiapk'
    app_channel = response.meta['app_channel']
    apk_name = response.meta['apk_name']
    app_name_version_info = html.xpath('//*[@id="appSoftName"]/text()').extract()[0].strip()
    app_name = app_name_version_info[:app_name_version_info.find('(')]

    try:
        app_link = 'http://apk.hiapk.com' + html.xpath('//*[@id="appInfoDownUrl"]/@href').extract()[0]
        app_download_times = html.xpath('//div[@class="code_box_border"]/div[@class="line_content"][3]/span[2]/text()').extract()[0]
    except:
        ## xpath有误。
        add_error_app_info(app_channel, app_name, '0')
        return None

    app_pn = html.xpath('//*[@id="appInfoDownUrl"]/@href').extract()[0].split('/')[-1]
    app_version = app_name_version_info[app_name_version_info.find('(')+1: -1]
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
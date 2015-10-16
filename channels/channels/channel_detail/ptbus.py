#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import *
from channels.settings import APK_DOWNLOAD_DIR


def send_ptbus_request(url, **kwargs):
    return Request(url,
                   meta=kwargs,
                   callback=send_ptbus_search_request)

def send_ptbus_search_request(response):
    log_page(response, 'send_ptbus_search_request.html')
    html = Selector(response)

    apk_name = response.meta['apk_name']
    url = html.xpath('//div[@class="input-sea"]/form/@action').extract()[0]
    s = html.xpath('//div[@class="input-sea"]/form/input[@name="s"]/@value').extract()[0]
    return FormRequest(url,
                  formdata={'q': apk_name, 's': s},
                  method='GET',
                  meta=response.meta,
                  callback=get_ptbus_search_list)


def get_ptbus_search_list(response):
    log_page(response, 'get_ptbus_search_list.html')

    url_list_xpath = '//*[@id="results"]/div[@tid="3"]/div[@class="result-list gameblock-result-list"]/div[@class="result-item result-game-item"]/div[@class="result-game-item-detail"]/h3/a/@href'
    name_list_xpath = '//*[@id="results"]/div[@tid="3"]/div[@class="result-list gameblock-result-list"]/div[@class="result-item result-game-item"]/div[@class="result-game-item-detail"]/h3/a/@title'
    func = get_ptbus_detail
    host = ''
    result = get_search_list(response, url_list_xpath, name_list_xpath, func, host)
    if type(result) == list:
        for r in result:
            yield r
    else:
        yield result


    # html = Selector(response)
    # detail_url = 'http://app.sogou.com' + html.xpath('//div[@class="search_list border_shadow"]/ul/li[1]/div[2]/h2/a/@href').extract()[0]
    # yield Request(detail_url, callback=get_sogou_detail)


def get_ptbus_detail(response):
    log_page(response, 'get_ptbus_detail.html')
    html = Selector(response)

    app_channel = response.meta['app_channel']
    apk_name = response.meta['apk_name']

    app_name = apk_name

    try:
        if 'http://www.ptbus.com/' in response.url:
            app_link = html.xpath('//a[@class="android Jsdownload"]/@href').extract()[0]
        else:
            app_link = html.xpath('//ul[@class="sum3_ul"]/li/a[@dltab="1"]/@href').extract()[0]
        app_download_times = ''
        if app_link[-4:] != '.apk':
            return None
    except:
        ## xpath有误。
        add_error_app_info(app_channel, app_name, '0')
        return None

    app_pn = ''
    app_version = ''
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
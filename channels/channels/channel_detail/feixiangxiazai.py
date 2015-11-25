#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import *
from channels.settings import APK_DOWNLOAD_DIR


def send_52z_request(url, **kwargs):
    apk_name = kwargs['apk_name']
    return FormRequest(url,
                       formdata={'keyword': apk_name.encode('gb2312')},
                       method='GET',
                       meta=kwargs,
                       callback=get_52z_search_list)

def get_52z_search_list(response):
    log_page(response, 'get_52z_search_list.html')

    url_list_xpath = '//div[@class="result_box"]/dl/dt/a/@href'
    name_list_xpath = '//div[@class="clsList"]/dl/dt/a/@title'
    func = get_52z_detail
    host = 'http://www.52z.com'
    result = get_search_list(response, url_list_xpath, name_list_xpath, func, host)
    if type(result) == list:
        for r in result:
            yield r
    else:
        yield result

    # html = Selector(response)
    # detail_url = 'http://apk.52z.com' + html.xpath('//div[@class="list-page"]/ul/li[1]/p/span[1]/a/@href').extract()[0]
    # yield Request(detail_url, callback=get_52z_detail)


def get_52z_detail(response):
    log_page(response, 'get_52z_detail.html')
    html = Selector(response)

    # app_channel = '52z'
    app_channel = response.meta['app_channel']
    apk_name = response.meta['apk_name']
    app_names = html.xpath('//h1[@class="title_h1"]/text()').extract()
    if app_names:
        app_name = app_names[0]
    else:
        app_name = apk_name

    try:
        app_links = html.xpath('//ul[@class="syGaosuDaList cBlack"]/li/a/@href').extract()
        if app_links:
            app_link = app_links[4]

            if app_link[-4:] != '.apk':
                return None
        else:
            return None
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
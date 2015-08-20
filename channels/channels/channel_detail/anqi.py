#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import download, log_page, get_search_list, add_error_app_info
from channels.settings import APK_DOWNLOAD_DIR

def send_anqi_request(url, **kwargs):
    apk_name = kwargs['apk_name']
    return FormRequest(url,
                  formdata={'select': 'all',
                            'keyword': apk_name},
                  method='POST',
                  meta=kwargs,
                  callback=get_anqi_search_list)

def get_anqi_search_list(response):
    log_page(response, 'get_anqi_search_list.html')

    url_list_xpath = '//div[@class="posts psiosnews"]/div[@class="box"]/div/h3/a/@href'
    name_list_xpath = '//div[@class="posts psiosnews"]/div[@class="box"]/div/h3/a/@title'
    func = get_anqi_detail
    host = 'http://www.apkcn.com'
    result = get_search_list(response, url_list_xpath, name_list_xpath, func, host)
    if type(result) == list:
        for r in result:
            yield r
    else:
        yield result


def get_anqi_detail(response):
    log_page(response, 'get_anqi_detail.html')
    html = Selector(response)

    # app_channel = 'anqi'
    app_channel = response.meta['app_channel']
    apk_name = response.meta['apk_name']
    app_name = apk_name

    try:
        toget_app_link = 'http://www.apkcn.com' + html.xpath('//div[@class="imginfo"]/p[2]/a/@href').extract()[0]
    except:
        ## xpath有误。
        add_error_app_info(app_channel, app_name, '0')
        yield None

    app_link = ''
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

    yield Request(toget_app_link, meta={'params_dic': params_dic},
                  callback=get_app_link)


def get_app_link(response):
    log_page(response, 'get_anqi_app_link.html')
    html = Selector(response)
    params_dic = response.meta['params_dic']

    try:
        app_link = html.xpath('//div[@class="dadadd"]/a/@href').extract()[0]
    except:
        ## xpath有误。
        add_error_app_info(params_dic['app_channel'], params_dic['app_name'], '0')
        return None

    params_dic['app_link'] = app_link

    return download(**params_dic)
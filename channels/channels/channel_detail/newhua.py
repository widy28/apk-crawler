#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import *
from channels.settings import APK_DOWNLOAD_DIR

def send_newhua_request(url, **kwargs):
    apk_name = kwargs['apk_name']
    url = url + apk_name
    return FormRequest(url,
                  method='GET',
                  meta=kwargs,
                  callback=get_newhua_search_list)


def get_newhua_search_list(response):
    log_page(response, 'get_newhua_search_list.html')

    # url_list_xpath = '//div[@class="con763 class-sub"]/dl/dd/div[@class="title"]/strong/a[1]/@href'
    # name_list_xpath = '//div[@class="con763 class-sub"]/dl/dd/div[@class="title"]/strong/a[1]/text()'
    url_list_xpath = '//div[@class="MlistA"]/div[@class="item"]/a[@class="det_area"]/@href'
    name_list_xpath = '//div[@class="MlistA"]/div[@class="item"]/a[@class="det_area"]/h4/text()'
    func = get_newhua_detail
    host = 'http://m.onlinedown.net'
    result = get_search_list(response, url_list_xpath, name_list_xpath, func, host)
    if type(result) == list:
        for r in result:
            yield r
    else:
        yield result


def get_newhua_detail(response):
    log_page(response, 'get_newhua_detail.html')
    html = Selector(response)

    apk_name = response.meta['apk_name']

    # app_channel = 'newhua'
    app_channel = response.meta['app_channel']
    # app_name = html.xpath('//div[@class="app_name"]/h2/span[1]/text()').extract()
    app_name = html.xpath('//div[@class="det_intro_box"]/div/h1/text()').extract()
    if app_name:
        app_name = app_name[0]
    else:
        app_name = ''

    print apk_name not in app_name,'88888888'*10

    # 判断apk_name 是否存在于app_name中，不存在就返回None
    if apk_name not in app_name:
        return None

    try:
        # toget_app_link = 'http://www.onlinedown.net' + html.xpath('//a[@class="megL"]/@href').extract()[0]
        # app_version = html.xpath('//div[@class="app_name"]/h2/span[2]/text()').extract()[0]

        app_link = html.xpath('//div[@class="r_area"]/a[2]/@href').extract()[0]
    except:
        ## xpath有误。
        add_error_app_info(app_channel, app_name, '0')
        return None

    app_pn = ''
    app_size = ''
    app_version = ''
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

    # return Request(toget_app_link, meta={'params_dic': params_dic}, callback=get_app_link)
    return download(**params_dic)

def get_app_link(response):
    log_page(response, 'get_newhua_app_link.html')
    html = Selector(response)
    app_link = html.xpath('//a[@class="other"]/@href').extract()[0]

    params_dic = response.meta['params_dic']
    params_dic['app_link'] = app_link

    return download(**params_dic)
#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import *
from channels.settings import APK_DOWNLOAD_DIR
import ctypes
import time

def send_yesky_request(url, **kwargs):
    apk_name = kwargs['apk_name']
    return FormRequest(url,
                       formdata={'wd': apk_name.encode('gbk')},
                       method='GET',
                       meta=kwargs,
                       callback=get_yesky_search_list)


def get_yesky_search_list(response):
    log_page(response, 'get_yesky_search_list.html')

    url_list_xpath = '//*[@id="main"]/div[1]/ul/li/h2/a/@href'
    name_list_xpath = '//*[@id="main"]/div[1]/ul/li/h2/a/text()'
    func = get_yesky_detail
    host = ''
    result = get_search_list(response, url_list_xpath, name_list_xpath, func, host)
    if type(result) == list:
        for r in result:
            yield r
    else:
        yield result

    # html = Selector(response)
    # detail_url = 'http://apk.yesky.com' + html.xpath('//div[@class="list-page"]/ul/li[1]/p/span[1]/a/@href').extract()[0]
    # yield Request(detail_url, callback=get_yesky_detail)


def get_yesky_detail(response):
    log_page(response, 'get_yesky_detail.html')
    html = Selector(response)

    # app_channel = 'yesky'
    app_channel = response.meta['app_channel']
    apk_name = response.meta['apk_name']
    app_names = html.xpath('//dl[@class="soft_name"]/dd/h1/a/span[1]/text()').extract()
    if app_names:
        app_name = app_names[0]
    else:
        app_name = apk_name

    try:
        toget_app_link = response.url.replace('.shtml', '_more.shtml')
    except:
        ## xpath有误。
        add_error_app_info(app_channel, app_name, '0')
        return None
    app_pn = ''
    app_version = ''
    app_size = ''
    save_dir = os.path.sep.join([APK_DOWNLOAD_DIR, apk_name])
    app_download_times = html.xpath('//div[@class="box_degest_left"]/p[9]/font/text()').extract()
    if app_download_times:
        app_download_times = app_download_times[0].strip()
    else:
        app_download_times = ''


    params_dic = {} # 参数字典
    params_dic['app_channel'] = app_channel     # 渠道
    params_dic['app_detail_url'] = response.url # apk下载页面
    params_dic['app_download_times'] = app_download_times  # apk下载次数
    params_dic['app_link'] = ''                 # apk下载链接
    params_dic['save_dir'] = save_dir           # 下载apk保存的目录
    params_dic['app_name'] = app_name           # 要下载的apk的应用名称
    params_dic['app_pn'] = app_pn               # apk包名
    params_dic['app_version'] = app_version     # apk版本号
    params_dic['app_size'] = app_size           # apk文件的大小

    return Request(toget_app_link,
                   meta=params_dic,
                   callback=get_yesky_app_link)


def get_yesky_app_link(response):
    log_page(response, 'get_yesky_app_link.html')

    params_dic = response.meta
    html = Selector(response)
    try:
        filepath_js = html.xpath('//*[@id="liantong1"]/@href').extract()[0]
        # print filepath_js,'000000000000000000000000000000000000'
        filepath = filepath_js[filepath_js.find('(')+2: filepath_js.find(')')-1]
        # print filepath,'==-=-=-=-=88888888888888888888888888888'
        if filepath[-4:] != '.apk':
            return None
    except:
        ## xpath有误。
        add_error_app_info(params_dic['app_channel'], params_dic['app_name'], '0')
        return None


    hexTime = hex(int(float(int(time.time()*1000))/1000))[2:]
    md5 = md5_str('yesky_download' + filepath + hexTime)

    app_link = 'http://cdn1.mydown.yesky.com/' + hexTime + '/' + md5 + filepath

    params_dic['app_link'] = app_link
    return download(**params_dic)


#十六进制->小数
def h2f(s):
    cp = ctypes.pointer(ctypes.c_longlong(s))
    fp = ctypes.cast(cp, ctypes.POINTER(ctypes.c_double))
    return fp.contents.valuex

#小数->十六进制
def f2h(s):
    fp = ctypes.pointer(ctypes.c_double(s))
    cp = ctypes.cast(fp, ctypes.POINTER(ctypes.c_longlong))
    return hex(cp.contents.value)

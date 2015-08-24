#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import *
from channels.settings import APK_DOWNLOAD_DIR
import re


def send_pconline_request(url, **kwargs):
    """
    参数顺序影响页面访问，2015-07-16号之前还是正常，之后就需要更改参数前后顺序。
    """
    # url = url + '?downloadType=%s&q=%s'%(u'Android下载'.encode('gbk'),apk_name.encode('gbk'))
    apk_name = kwargs['apk_name']
    return FormRequest(url,
                    formdata={'q': apk_name.encode('gbk'), 'downloadType': u'Android下载'.encode('gbk'), 'scope=': ''},
                    method='GET',
                    meta=kwargs,
                    callback=get_pconline_search_list)


def get_pconline_search_list(response):
    log_page(response, 'get_pconline_search_list.html')

    url_list_xpath = '//div[@class="dlList"]/ul/li/dl/dt/a/@href'
    name_list_xpath = '//div[@class="dlList"]/ul/li/dl/dt/a/@title'
    func = get_pconline_detail
    host = ''
    result = get_search_list(response, url_list_xpath, name_list_xpath, func, host)
    if type(result) == list:
        for r in result:
            yield r
    else:
        yield result


def get_pconline_detail(response):
    log_page(response, 'get_pconline_detail.html')
    html = Selector(response)

    # 找到页面获取token的js：
    """
    (function(){

            setTimeout(function(){

                $.getScript('http://dlc2.pconline.com.cn/dltoken/86771_genLink.js');

            },1000);

        })();
    """

    # app_channel = 'pconline'
    app_channel = response.meta['app_channel']
    apk_name = response.meta['apk_name']
    app_name = response.meta['app_name']

    try:
        app_link = html.xpath('//a[@class="btn sbDownload"]/@href').extract()[0]
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
    params_dic['app_link'] = app_link           # apk下载链接
    params_dic['save_dir'] = save_dir           # 下载apk保存的目录
    params_dic['app_name'] = app_name           # 要下载的apk的应用名称
    params_dic['app_pn'] = app_pn               # apk包名
    params_dic['app_version'] = app_version     # apk版本号
    params_dic['app_size'] = app_size           # apk文件的大小

    return download(**params_dic)
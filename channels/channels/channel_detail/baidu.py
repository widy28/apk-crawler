#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import *
from channels.settings import APK_DOWNLOAD_DIR

def send_baidu_request(url, **kwargs):
    apk_name = kwargs['apk_name']
    return FormRequest(url,
                      formdata={'wd': apk_name,
                                'data_type': 'app',
                                'f': 'header_all@input@btn_search'},
                      method='GET',
                      meta=kwargs,
                      callback=get_baidu_search_list)


def get_baidu_search_list(response):
    log_page(response, 'get_baidu_search_list.html')
    """
    百度搜索，会把完全匹配的应用置顶，需要先判断是否存在完全匹配的apk的xpath是否存在，
    如果不存在，再去找相关联的apk列表的xpath
    """
    url_list_xpath = '//ul[@class="app-list"]/li/div[@class="app"]/div[@class="info"]/div[@class="top"]/a/@href'
    name_list_xpath = '//ul[@class="app-list"]/li/div[@class="app"]/div[@class="little-install"]/a/@data_name'
    func = get_baidu_detail
    host = 'http://shouji.baidu.com'
    result = get_search_list(response, url_list_xpath, name_list_xpath, func, host)
    if type(result) == list:
        for r in result:
            yield r
    else:
        yield result



def get_baidu_detail(response):

    html = Selector(response)
    apk_name = response.meta['apk_name']

    app_name = html.xpath('//div[@class="area-download"]/a/@data_name').extract()[0]
    app_pn = html.xpath('//div[@class="area-download"]/a/@data_package').extract()[0]
    app_link = html.xpath('//div[@class="area-download"]/a/@data_url').extract()[0]
    app_version = html.xpath('//div[@class="area-download"]/a/@data_versionname').extract()[0]
    app_size = html.xpath('//div[@class="area-download"]/a/@data_size').extract()[0]
    app_download_times = html.xpath('//span[@class="download-num/text()"]').extract()[0].split(': ')[1]


    app_channel = response.meta['app_channel']

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
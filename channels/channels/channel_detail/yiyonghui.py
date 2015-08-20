#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import download, log_page, get_search_list
from channels.settings import APK_DOWNLOAD_DIR


def send_yiyonghui_request(url, **kwargs):
    apk_name = kwargs['apk_name']
    url = url + '/%s-1/'%(apk_name)
    return FormRequest(url,
                    method='get',
                    meta=kwargs,
                    callback=get_yiyonghui_search_list)


def get_yiyonghui_search_list(response):
    log_page(response, 'get_yiyonghui_search_list.html')

    url_list_xpath = '//div[@class="app_all_list"]/dl/dd/div[@class="app_txt z"]/p[1]/a/@href'
    name_list_xpath = '//div[@class="app_all_list"]/dl/dd/div[@class="app_txt z"]/p[1]/a/text()'
    func = get_yiyonghui_detail
    host = ''
    result = get_search_list(response, url_list_xpath, name_list_xpath, func, host)
    if type(result) == list:
        for r in result:
            yield r
    else:
        yield result

    # html = Selector(response)
    # detail_url = html.xpath('//div[@class="app_all_list"]/dl/dd[1]/div[2]/p[1]/a/@href').extract()[0]
    # yield Request(detail_url,
    #               meta=response.meta,
    #               callback=get_yiyonghui_detail)


def get_yiyonghui_detail(response):
    log_page(response, 'get_yiyonghui_detail.html')
    html = Selector(response)

    # app_channel = 'yiyonghui'
    app_channel = response.meta['app_channel']
    apk_name = response.meta['apk_name']

    app_name = apk_name
    app_link = 'http://www.anzhuoapk.com' + html.xpath('//div[@class="content1_bottom"]/a[1]/@href').extract()[0]
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
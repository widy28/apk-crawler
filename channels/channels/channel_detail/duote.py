#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import *
from channels.settings import APK_DOWNLOAD_DIR
import re

def send_duote_request(url, **kwargs):
    # apk_name = apk_name.decode("UTF-8")
    apk_name = kwargs['apk_name']
    apk_name = apk_name.encode('gbk')
    return FormRequest(url,
                  formdata={'searchType': '', 'so': apk_name},
                  method='GET',
                  meta=kwargs,
                  callback=get_duote_search_list)


def get_duote_search_list(response):
    log_page(response, 'get_duote_search_list.html')

    url_list_xpath = '//*[@id="Mlist"]/div/div[@class="Mimg"]/a/@href'
    name_list_xpath = '//*[@id="Mlist"]/div/div[@class="Mimg"]/img/@alt'
    func = get_duote_detail
    host = 'http://www.duote.com'
    result = get_search_list(response, url_list_xpath, name_list_xpath, func, host)
    if type(result) == list:
        for r in result:
            yield r
    else:
        yield result


    # html = Selector(response)
    # detail_url = 'http://www.duote.com' + html.xpath('//*[@id="Mlist"]/div/div[1]/a/@href').extract()[0]
    # yield Request(detail_url, callback=get_duote_detail)


def get_duote_detail(response):
    log_page(response, 'get_duote_detail.html')
    html = Selector(response)

    # app_channel = 'duote'
    apk_name = response.meta['apk_name']
    app_channel = response.meta['app_channel']
    app_name = html.xpath('//div[@class="tit_area clearfix"]/h1/text()').extract()[0]
    app_link = get_app_link(response.body)
    app_pn = ''

    try:
        app_version = html.xpath('//ul[@class="prop_area"]/li[1]/text()').extract()[0].split(u'：')[1]
    except:
        ## xpath有误。
        add_error_app_info(app_channel, app_name, '0')
        return None

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


def get_app_link(content):
    p = re.compile("var sUrl = '(.*?)'")
    res = re.search(p, content)
    sUrl = res.group().split('\'')[1]

    if sUrl.find('/') == -1:
        app_link = 'http://app.2345.cn' + '/appsoft/' + sUrl
    else:
        app_link = 'http://app.2345.cn' + "/" + sUrl

    return app_link
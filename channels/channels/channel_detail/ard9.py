#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import *
from channels.settings import APK_DOWNLOAD_DIR


def send_ard9_request(url, **kwargs):
    apk_name = kwargs['apk_name']
    return FormRequest(url,
                       method='GET',
                       meta=kwargs,
                       callback=get_ard9_formdata)


def get_ard9_formdata(response):
    log_page(response, 'get_ard9_formdata.html')
    html = Selector(response)
    action = 'http://www.ard9.com' + html.xpath('//form[@id="form1"]/@action').extract()[0]
    domains = html.xpath('//form[@id="form1"]/dl/dd/input[@name="domains"]/@value').extract()[0]
    kwtype = html.xpath('//form[@id="form1"]/dl/dd/input[@name="kwtype"]/@value').extract()[0]
    searchtype = html.xpath('//form[@id="form1"]/dl/dd/input[@name="searchtype"]/@value').extract()[0]
    client = html.xpath('//form[@id="form1"]/dl/dd/input[@name="client"]/@value').extract()[0]
    forid = html.xpath('//form[@id="form1"]/dl/dd/input[@name="forid"]/@value').extract()[0]
    ie = html.xpath('//form[@id="form1"]/dl/dd/input[@name="ie"]/@value').extract()[0]
    oe = html.xpath('//form[@id="form1"]/dl/dd/input[@name="oe"]/@value').extract()[0]
    safe = html.xpath('//form[@id="form1"]/dl/dd/input[@name="safe"]/@value').extract()[0]
    cof = html.xpath('//form[@id="form1"]/dl/dd/input[@name="cof"]/@value').extract()[0]
    hl = html.xpath('//form[@id="form1"]/dl/dd/input[@name="hl"]/@value').extract()[0]

    formdata = {'q': response.meta['apk_name'].encode('gb2312'),
                'domains': domains,
                'kwtype': kwtype,
                'searchtype': searchtype,
                'client': client,
                'forid': forid,
                'ie': ie,
                'oe': oe,
                'safe': safe,
                'cof': cof,
                'hl': hl}

    return FormRequest(action,
                       formdata=formdata,
                       method='GET',
                       meta=response.meta,
                       callback=get_ard9_search_list)


def get_ard9_search_list(response):
    log_page(response, 'get_ard9_search_list.html')

    url_list_xpath = '//div[@class="resultlist"]/ul/li/h3/a/@href'
    name_list_xpath = '//div[@class="resultlist"]/ul/li/h3/a/text()'
    func = get_ard9_detail
    host = 'http://www.ard9.com'
    result = get_search_list(response, url_list_xpath, name_list_xpath, func, host)
    if type(result) == list:
        for r in result:
            yield r
    else:
        yield result

    # html = Selector(response)
    # detail_url = 'http://apk.ard9.com' + html.xpath('//div[@class="list-page"]/ul/li[1]/p/span[1]/a/@href').extract()[0]
    # yield Request(detail_url, callback=get_ard9_detail)


def get_ard9_detail(response):
    log_page(response, 'get_ard9_detail.html')
    html = Selector(response)

    # app_channel = 'ard9'
    app_channel = response.meta['app_channel']
    apk_name = response.meta['apk_name']
    app_names = html.xpath('//div[@class="info_title"]/h1/text()').extract()
    if app_names:
        app_name = app_names[0].strip()
    else:
        app_name = apk_name

    try:
        toget_app_link = 'http://www.ard9.com' + html.xpath('//*[@id="con_down_1"]/ul/li[1]/a/@href').extract()[0]
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
    params_dic['app_link'] = ''                 # apk下载链接
    params_dic['save_dir'] = save_dir           # 下载apk保存的目录
    params_dic['app_name'] = app_name           # 要下载的apk的应用名称
    params_dic['app_pn'] = app_pn               # apk包名
    params_dic['app_version'] = app_version     # apk版本号
    params_dic['app_size'] = app_size           # apk文件的大小

    return Request(toget_app_link,
                   meta=params_dic,
                   callback=get_ard9_app_link)

def get_ard9_app_link(response):
    log_page(response, 'get_ard9_app_link.html')
    params_dic = response.meta
    html = Selector(response)
    try:
        app_link = 'http://www.ard9.com' + html.xpath('//div[@class="minh"]/div[1]/p/a/@href').extract()[0]
    except:
        ## xpath有误。
        add_error_app_info(params_dic['app_channel'], params_dic['app_name'], '0')
        return None

    params_dic['app_link'] = app_link
    return download(**params_dic)
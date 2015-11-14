#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import *
from channels.settings import APK_DOWNLOAD_DIR


def send_mumayibbs_request(url, **kwargs):
    # apk_name = kwargs['apk_name']
    kwargs['cookiejar'] = 0
    return FormRequest(url,
                    formdata={'username': 'widy28@163.com', 'password': '2322871hzb',
                    'quickforward': 'yes', 'handlekey': 'ls'},
                    method='POST',
                    meta=kwargs,
                    callback=get_mumayibbs_search_formhash)

def get_mumayibbs_search_formhash(response):
    log_page(response, 'get_mumayibbs_search_formhash.html')
    url = 'http://bbs.mumayi.com/search.php?mod=forum'
    yield FormRequest(url,
                    method='get',
                    meta=response.meta,
                    callback=get_mumayibbs_search)

def get_mumayibbs_search(response):
    log_page(response, 'get_mumayibbs_search.html')
    html = Selector(response)
    formhash = html.xpath('//input[@name="formhash"]/@value').extract()[0]

    url = response.url
    kw = response.meta['apk_name'].encode('gbk')
    yield FormRequest(url,
                      formdata={'srchtxt': kw, 'formhash': formhash, 'searchsubmit': 'yes'},
                      method='GET',
                      meta=response.meta,
                      callback=get_mumayibbs_search_list)


def get_mumayibbs_search_list(response):
    log_page(response, 'get_mumayibbs_search_list.html')

    url_list_xpath = '//div[@id="threadlist"]/ul/li[@class="pbw"]/h3/a/@href'
    name_list_xpath = '//div[@id="threadlist"]/ul/li[@class="pbw"]/h3/a/text()'
    func = get_mumayibbs_detail
    host = 'http://bbs.mumayi.com/'
    result = get_search_list(response, url_list_xpath, name_list_xpath, func, host)
    if type(result) == list:
        for r in result:
            yield r
    else:
        yield result

    # html = Selector(response)
    # detail_url = html.xpath('/html/body/div[1]/div[4]/div[1]/div[1]/div[2]/div/div/ul/li[1]/div/div/div[2]/h3/a/@href').extract()[0]
    # yield Request(detail_url, callback=get_mumayibbs_detail)


def get_mumayibbs_detail(response):
    log_page(response, 'get_mumayibbs_detail.html')
    html = Selector(response)

    # app_channel = 'mumayibbs'
    app_channel = response.meta['app_channel']
    apk_name = response.meta['apk_name']
    app_name = html.xpath('//h1[@class="iappname hidden fl"]/text()').extract()[0]
    try:
        app_link = html.xpath('//a[@class="download fl"]/@href').extract()[0]
        app_pn = html.xpath('//ul[@class="author"]/li[2]/text()').extract()[0]
    except:
        ## xpath有误。
        add_error_app_info(app_channel, app_name, '0')
        return None

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
    params_dic['app_version'] = app_version     # apk版本号
    params_dic['app_pn'] = app_pn               # apk包名
    params_dic['app_size'] = app_size           # apk文件的大小

    return download(**params_dic)
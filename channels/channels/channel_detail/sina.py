#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import download, log_page, get_search_list
from channels.settings import APK_DOWNLOAD_DIR
import requests

def send_sina_request(url, **kwargs):
    apk_name = kwargs['apk_name']
    apk_name = apk_name.encode('gbk')
    return FormRequest(url,
                  formdata={'keyword': apk_name, 'submit.x': '3', 'submit.y': '21'},
                  method='GET',
                  meta=kwargs,
                  callback=get_sina_search_list)


def get_sina_search_list(response):
    log_page(response, 'get_sina_search_list.html')
    html = Selector(response)
    sina_android_list_url = 'http://down.tech.sina.com.cn' + html.xpath('//*[@id="hover"]/a/@href').extract()[0]
    yield Request(sina_android_list_url, meta=response.meta, callback=get_sina_android_list)


def get_sina_android_list(response):
    log_page(response, 'get_sina_android_list.html')

    url_list_xpath = '/html/body/div/div/h3/a/@href'
    name_list_xpath = '/html/body/div/div/h3/a/text()'
    func = get_sina_detail
    host = 'http://down.tech.sina.com.cn'
    result = get_search_list(response, url_list_xpath, name_list_xpath, func, host)
    if type(result) == list:
        for r in result:
            yield r
    else:
        yield result

    # html = Selector(response)
    # detail_url = 'http://down.tech.sina.com.cn' + html.xpath('/html/body/div[1]/a/@href').extract()[0]
    # yield Request(detail_url, callback=get_sina_detail)


def get_sina_detail(response):
    log_page(response, 'get_sina_detail.html')
    html = Selector(response)

    # app_channel = 'sina'
    apk_name = response.meta['apk_name']
    app_channel = response.meta['app_channel']
    app_name = html.xpath('//div[@class="tit_01"]/h2/text()').extract()[0]
    ip = get_ip()
    app_link = 'http://down.tech.sina.com.cn' + html.xpath('//*[@id="downurl_link"]/@href').extract()[0]
    print app_link,'11111111111111111111111------------------'
    app_pn = ''
    app_version = html.xpath('//ul[@class="zcwords  clearfix"]/li[2]/p[1]/text()').extract()[0].split(u'：')[1]
    app_size = ''
    save_dir = os.path.sep.join([APK_DOWNLOAD_DIR, apk_name])
    app_download_times = html.xpath()('//ul[@class="zcwords  clearfix"]/li[7]/text()').extract()[0].split(u'总计：')[1]


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

    yield Request(app_link, meta={'params_dic': params_dic}, callback=get_app_download_link)


def get_app_download_link(response):
    params_dic = response.meta['params_dic']
    params_dic['app_link'] = response.url
    print response.url,'------------------------'
    return download(**params_dic)


def get_ip():
    r = requests.get('http://sinastorage.com/?extra&op=selfip.js&cb=downWithIp')
    ip = r.content.split("'")[1]
    return ip
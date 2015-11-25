#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import *
from channels.settings import APK_DOWNLOAD_DIR


def send_cr173_request(url, **kwargs):
    apk_name = kwargs['apk_name']
    return FormRequest(url,
                       method='GET',
                       meta=kwargs,
                       callback=get_cr173_search_formdata)


def get_cr173_search_formdata(response):
    log_page(response, 'get_search_formdata.html')
    html = Selector(response)

    search_url = html.xpath('//form[@id="topForm"]/@action').extract()
    s = html.xpath('//form[@id="topForm"]/input[@name="s"]/@value').extract()

    if search_url and s:
        return FormRequest(search_url[0],
                           formdata={'q': response.meta['apk_name'], 's': s[0], 'nsid': '2'},
                           method='GET',
                           meta=response.meta,
                           callback=get_cr173_search_list)

    else:
        return None


def get_cr173_search_list(response):
    log_page(response, 'get_cr173_search_list.html')

    url_list_xpath = '//*[@id="results"]/div/h3/a/@href'
    name_list_xpath = '//*[@id="results"]/div/h3/a/text()'
    func = get_cr173_detail
    host = ''
    result = get_search_list(response, url_list_xpath, name_list_xpath, func, host)
    if type(result) == list:
        for r in result:
            yield r
    else:
        yield result

    # html = Selector(response)
    # detail_url = 'http://apk.cr173.com' + html.xpath('//div[@class="list-page"]/ul/li[1]/p/span[1]/a/@href').extract()[0]
    # yield Request(detail_url, callback=get_cr173_detail)


def get_cr173_detail(response):
    log_page(response, 'get_cr173_detail.html')
    html = Selector(response)

    # app_channel = 'cr173'
    app_channel = response.meta['app_channel']
    apk_name = response.meta['apk_name']
    app_names = html.xpath('//*[@id="softtitle"]/text()').extract()
    if app_names:
        app_name = app_names[0]
    else:
        app_name = apk_name

    try:
        ul_data = html.xpath('//ul[@class="ul_Address"]/script[1]/text()').extract()[0]
        link = ul_data[ul_data.find(':')+2: ul_data.find(',')-1]
        app_link = 'http://xz.cr173.com' + link
        if app_link[-4:] != '.apk':
            return None
    except:
        ## xpath有误。
        add_error_app_info(app_channel, app_name, '0')
        return None
    app_pn = ''
    app_version = ''
    app_size = ''
    save_dir = os.path.sep.join([APK_DOWNLOAD_DIR, apk_name])
    app_download_times = html.xpath('//dl[@class="dl-info fl"]/dd/text()').extract()
    if app_download_times:
        app_download_times = app_download_times[0]
    else:
        app_download_times = ''


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
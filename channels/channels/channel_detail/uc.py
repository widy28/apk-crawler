#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import *
from channels.settings import APK_DOWNLOAD_DIR


def send_uc_request(url, **kwargs):
    apk_name = kwargs['apk_name']
    url = url+ '?system=source&module=search&action=sm&app=&f=12_0_0_0_0&uc_param_str=dnfrpfbives11scpmibtbmntnisieigd&keyword='+apk_name
    return FormRequest(url,
                       method='GET',
                       meta=kwargs,
                       callback=get_uc_search_list)


def get_uc_search_list(response):
    log_page(response, 'get_uc_search_list.html')

    url_list_xpath = '//ul[@class="J_ajaxWrap"]/li/a/@href'
    name_list_xpath = '//ul[@class="J_ajaxWrap"]/li/dl/dt/span/span/text()'
    func = get_uc_detail
    host = ''
    result = get_search_list(response, url_list_xpath, name_list_xpath, func, host)
    if type(result) == list:
        for r in result:
            yield r
    else:
        yield result


def get_uc_detail(response):
    log_page(response, 'get_uc_detail.html')
    html = Selector(response)

    # app_channel = 'uc'
    apk_name = response.meta['apk_name']
    app_channel = response.meta['app_channel']
    app_name = html.xpath('//h3[@class="detail-info-title"]/text()').extract()
    if app_name:
        app_name = app_name[0]
    else:
        app_name = apk_name

    try:
        app_id = html.xpath('//*[@id="btn-down"]/@data-appid').extract()[0]

        app_link = 'http://server.m.pp.cn/download/apk?appId={app_id}&ch_src=sm&ch=uc&query={apk_name}&uc_param_str=dnfrpfbivesscpmibtbmntnisieigd&custom=1'.format(app_id=app_id, apk_name=apk_name)
        print app_link,'==================='
    except:
        ## xpath有误。
        add_error_app_info(app_channel, app_name, '0')
        return None

    app_pn = ''
    # app_version = html.xpath('//*[@id="wrapper"]/div[2]/div/div[1]/div[2]/ul/li[1]/text()').extract()[0].split(u'：')[1]
    app_version = ''
    app_size = ''
    save_dir = os.path.sep.join([APK_DOWNLOAD_DIR, apk_name])
    app_download_times = html.xpath('//span[@class="detail-info-down"]/text()').extract()
    if app_download_times:
        app_download_times = app_download_times[0].split('|')[0].strip()
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
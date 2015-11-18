#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.http import Request, Response, FormRequest
import os
from channels.conf import download, log_page, get_search_list, add_error_app_info
from channels.settings import APK_DOWNLOAD_DIR

def send_aliexpress_request(url, **kwargs):
    return FormRequest(url,
                  method='GET',
                  meta=kwargs,
                  callback=get_aliexpress_activity)


def get_aliexpress_activity(response):
    log_page(response, 'get_aliexpress_activity.html')
    html = Selector(response)

    activity = html.xpath('//*[@id="key-visual-main"]/div/div/ul/li[2]/a/@href').extract()[0]
    yield Request(activity, callback=get_aliexpress_detail)

def get_aliexpress_detail(response):
    log_page(response, 'get_aliexpress_detail.html')
    html = Selector(response)
    urls = html.xpath('//div[@class="press-area-wrap"]/a/@href').extract()

    for u in urls:
        yield Request(u, callback=get_detail_page)


def get_detail_page(response):
    log_page(response, response.url[-8:]+'.html')
    html = Selector(response)

    price = html.xpath('//span[@id="sku-discount-price"]/text()').extract()
    print price,'-----'

    score = html.xpath('//div[@class="seller-score"]/a[@class="seller-score-lnk"]/b/text()').extract()

    print score,'====='
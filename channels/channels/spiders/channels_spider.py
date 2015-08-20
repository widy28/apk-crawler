#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from scrapy.contrib.spiders import CrawlSpider
from channels.settings import CHANNELS_URL_FUNCTION_DICT
from channels.channel_detail import *


class ChannelSpider(CrawlSpider):

    def __init__(self, apk_name='', **kwargs):
        super(ChannelSpider, self).__init__()
        # print unicode(app_name, 'gbk') == APP_LIST[0]
        # print kwargs,'-k-k-k-k-'
        # self.apk_name = kwargs['apk_name']
        # self.apk_name = unicode(apk_name, 'gbk')
        self.apk_name = apk_name
        self.start_urls = CHANNELS_URL_FUNCTION_DICT.keys()

    name = 'channels'

    def start_requests(self):
        for url in self.start_urls:
            f = CHANNELS_URL_FUNCTION_DICT.get(url)[1]
            kwargs = {'apk_name': self.apk_name, 'app_channel': CHANNELS_URL_FUNCTION_DICT.get(url)[0]}
            yield eval(f)(url, **kwargs)
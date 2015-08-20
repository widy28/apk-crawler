#!/usr/local/bin/python
# -*- coding:utf-8 -*-

from datetime import datetime

from scrapy import signals
from twisted.internet.task import LoopingCall
# from xxx.utils.tb_utils import *
from channels import settings
from channels.conf import createMongodbClient

class SpiderDetails(object):
    """Extension for collect spider information like start/stop time."""

    update_interval = 5  # in seconds

    def __init__(self, crawler, **kwargs):
        # keep a reference to the crawler in case is needed to access to more information
        self.crawler = crawler
        # keep track of polling calls per spider
        self.pollers = {}

        self.collection = createMongodbClient(settings.MONGODB_APP_TASK_COLLECTION)

    @classmethod
    def from_crawler(cls, crawler):
        instance = cls(crawler)
        crawler.signals.connect(instance.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(instance.spider_closed, signal=signals.spider_closed)
        return instance

    def spider_opened(self, spider):
        # start activity poller
        print '======================='

        self.collection.update({'app_name': spider.apk_name},
                               {'$set': {'status': '1'}})


        poller = self.pollers[spider.name] = LoopingCall(self.spider_update, spider)
        poller.start(self.update_interval)

    def spider_closed(self, spider, reason):
        # 更新状态，通知与记录状态
        # key 转换，不然这样的stats.downloader/exception_type_count/twisted.web._newclient.ResponseNeverReceived会提示错误
        sys_stats = self.crawler.stats.get_stats()
        tb_stats = {}
        print sys_stats,'sssssssssssssssssssssssssss'
        for (k,v) in sys_stats.items():
            if '.' in k:
                k = str(k).replace('.', '*')
            tb_stats[k] = v

        task = self.collection.find({'app_name': spider.apk_name})
        self.collection.update({'app_name': spider.apk_name},
                               {'$set': {'status': '2',
                                'start_time': tb_stats['start_time'].strftime('%Y-%m-%d %H:%M:%S %f'),
                                'end_time': tb_stats['finish_time'].strftime('%Y-%m-%d %H:%M:%S %f')}})
        # task['status'] = '2'
        # task['start_time'] = tb_stats['start_time']
        # task['end_time'] = tb_stats['finish_time']


        print spider.apk_name,'uuuuuuuuuuuuuuuu'
        print tb_stats,'tttttttttttttttttttt'



        # print spider.name,'=-=-=-=-=-=-=-=-=-=-='
        # updateSpiderTrack(spider.name, tb_stats)
        # remove and stop activity poller
        poller = self.pollers.pop(spider.name)
        poller.stop()

    def spider_update(self, spider):
        pass

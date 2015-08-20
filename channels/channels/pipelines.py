#!/usr/local/bin/python
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from channels import settings
from scrapy.exceptions import DropItem
from scrapy import log
from conf import createMongodbClient

class MongoDBPipeline(object):

    def __init__(self):
        self.collection = createMongodbClient(settings.MONGODB_COLLECTION)

    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:
            # 根据渠道名，包名，版本号，apk的MD5码
            ishave = self.collection.find({'app_channel': item['app_channel'],\
                                           'app_pn': item['app_pn'],\
                                           'app_version': item['app_version'],\
                                           'app_MD5': item['app_MD5']}).count()
            print ishave, '-----------------------count'
            if not ishave:
                try:
                    self.collection.insert(dict(item))
                    log.msg("app_info added to MongoDB database!",
                        level=log.DEBUG, spider=spider)
                except:
                    ## todo 入库异常记录
                    pass
        return item

class ChannelsPipeline(object):
    def process_item(self, item, spider):
        return item

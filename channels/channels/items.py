#!/usr/local/bin/python
# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

"""
/telnet.py", line 63, in stop_listening
    self.port.stopListening()
AttributeError: TelnetConsole instance has no attribute 'port'

"""


class ChannelsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    app_channel = scrapy.Field() # 渠道名称
    app_name = scrapy.Field()    # 名称
    app_size = scrapy.Field()    # 大小
    app_version = scrapy.Field() # 版本号
    app_link = scrapy.Field()    # 下载链接
    app_pn = scrapy.Field()      # 包名
    app_signMD5 = scrapy.Field() # 签名的md5码
    app_signFileMD5 = scrapy.Field()     # 签名文件的md5码
    app_MD5 = scrapy.Field()     # app的md5码
    app_icon = scrapy.Field()    # 图标文件路径
    app_file = scrapy.Field()    # apk文件的存储路径


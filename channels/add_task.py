#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from get_task import MongoDBTaskClient
import time

if __name__ == '__main__':
    mt = MongoDBTaskClient()

    mt.collect_drop()
    mt.insert_task(u'招商银行')
    # # time.sleep(60)
    # mt.insert_task(u'微信')
    # # # time.sleep(60)
    # mt.insert_task(u'建设银行')
    # time.sleep(60)
    # # # time.sleep(60)
    # mt.insert_task(u'民生银行')
    # # time.sleep(60)
    # mt.insert_task(u'微信锁')
    mt.insert_task(u'微信电话本')
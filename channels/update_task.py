#!/usr/local/bin/python
# -*- coding: utf-8 -*-
__author__ = 'widy28'
from get_task import MongoDBTaskClient
import subprocess
from multiprocessing import Process
import datetime, time


# # 写数据进程执行的代码:
# def write(q):
#     mtc = MongoDBTaskClient()
#     while True:
#         # print('Process to write: %s' % os.getpid())
#         time.sleep(2)
#         tasks = mtc.get_task()
#         # print 'Queue is empty:--', q.empty()
#         # print 'Queue qsize:--', q.qsize()
#         # print 'Tasks count:--',tasks.count()
#
#         # 如果队列为空，则取tasks.linit(3)
#         # 如果队不为空，判断q.qsize()是否小于3,小于3,则取tasks.linmit(3-q.qsize())添加到q.
#         # 如果tasks.count()为0,则循环等待。。
#         if q.empty():
#             if tasks.count() > n:
#                 tasks = tasks.limit(n)
#         else:
#             if q.qsize() < n:
#                 tasks = tasks.limit(n-q.qsize())
#         for t in tasks:
#             if not q.full():
#                 # print '22222'
#                 app_name = t['app_name']
#                 q.put(app_name)


# def update():
#     mt = MongoDBTaskClient()
#     tasks_list = mt.get_need_update_task()
#     while True:
#         time.sleep(2)
#         if tasks_list:
#             for t in tasks_list:
#                 if t['status'] == '3':
#                     app_name = t['app_name']
#                     p = subprocess.Popen('scrapy crawl channels -a apk_name=%s --logfile=log/%s.log'%(app_name, app_name), shell=True)
#

if __name__ == '__main__':
    # p = Process(target=update)
    # p.start()
    # p.join()

    mt = MongoDBTaskClient()
    tasks_list = mt.get_need_update_task()
    # print tasks_list,'--------------'

    if tasks_list:
        for t in tasks_list:
            app_name = t['app_name']
            p = subprocess.Popen('scrapy crawl channels -a apk_name=%s --logfile=log/%s.log'%(app_name, app_name), shell=True)

    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %f')
    with open('test_crontab.log', 'a') as f:
        f.write(now + '\n')

#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from gevent import monkey; monkey.patch_socket()
from pymongo import MongoClient
from channels import settings
import time
import os
import gevent
from multiprocessing import Pool, Process, Queue
import subprocess
# import Queue
import random
from channels.conf import createMongodbClient
import datetime

TASK_STATUS = {'0': u'等待中',
               '1': u'爬取中',
               '2': u'已完成',}

class MongoDBTaskClient(object):

    def __init__(self):
        # connection = MongoClient(
        #     settings.MONGODB_SERVER,
        #     settings.MONGODB_PORT
        # )
        # db = connection[settings.MONGODB_DB]
        # db.authenticate(settings.MONGODB_DB_USERNAME, settings.MONGODB_DB_PWD)
        self.collection = createMongodbClient(settings.MONGODB_APP_TASK_COLLECTION)

    def get_task(self):
        # 等待的任务
        tasks = self.collection.find({'status': '0'})
        return tasks

    def insert_task(self, app_name):
        is_have_tasl = self.collection.find({'app_name': app_name}).count()
        if not is_have_tasl:
            self.collection.insert({'app_name': app_name,
                                    'status': '0',
                                    'start_time': '',
                                    'update_time': '',
                                    'end_time': '',})

    def find_one_task(self, app_name):
        return self.collection.find_one({'app_name': app_name})

    def collect_drop(self):
        self.collection.drop()

    def get_need_update_task(self):
        # 获取状态为 '2'的所有任务--已完成的任务
        tasks = self.collection.find({'status': '2'})
        tasks_list = []
        if tasks:
            for t in tasks:
                print t
                """
                先判断update_time是否为空，为空则根据end_time去计算是否达到2周的更新时间
                """
                now = datetime.datetime.now()
                update_time = t['update_time']
                end_time = t['end_time']
                if update_time:
                    update_time = datetime.datetime.strptime(update_time, '%Y-%m-%d %H:%M:%S %f')
                    ## todo 修改(now - update_time).days
                    # d = (now - update_time).seconds/60
                    d = (now - update_time).days
                else:
                    end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S %f')
                    # d = (now - end_time).seconds/60
                    d = (now - end_time).days

                ## todo 修改14天
                print d
                if d >= 14:
                    tasks_list.append(t)
        return tasks_list

# 写数据进程执行的代码:
def write(q):
    mtc = MongoDBTaskClient()
    while True:
        # print('Process to write: %s' % os.getpid())
        time.sleep(2)
        tasks = mtc.get_task()
        # print 'Queue is empty:--', q.empty()
        # print 'Queue qsize:--', q.qsize()
        # print 'Tasks count:--',tasks.count()

        # 如果队列为空，则取tasks.linit(3)
        # 如果队不为空，判断q.qsize()是否小于3,小于3,则取tasks.linmit(3-q.qsize())添加到q.
        # 如果tasks.count()为0,则循环等待。。
        if q.empty():
            if tasks.count() > n:
                tasks = tasks.limit(n)
        else:
            if q.qsize() < n:
                tasks = tasks.limit(n-q.qsize())
        for t in tasks:
            if not q.full():
                # print '22222'
                app_name = t['app_name']
                q.put(app_name)
        # print '3333'


        # g = gevent.spawn(read, q)
        # g.join()

# 读数据进程执行的代码:
def read(q):
    mtc = MongoDBTaskClient()
    while True:
        # print('Process to read: %s' % os.getpid())
        time.sleep(2)
        # print q.qsize(),'*****************************'
        for i in range(q.qsize()):
            # if not q.empty():
            # print '44444'
            app_name = q.get()
            # print q.empty(),'====================='

            # pr = Process(target=os.system, args=('scrapy crawl channels -a apk_name=' + app_name.encode('utf8'),))
            # print('Process to os.system: %s' % os.getpid())
            # pr.start()
            # pr.join()
            t = mtc.find_one_task(app_name)
            if t['status'] == '0':
                p = subprocess.Popen('scrapy crawl channels -a apk_name=%s --logfile=log/%s.log'%(app_name, app_name), shell=True)

            # print p.poll(),'------------------------------------------'
    # else:
    #     break

if __name__ == '__main__':
    # 父进程创建Queue，并传给各个子进程：
    n = 3
    q = Queue(maxsize=n)

    pw = Process(target=write, args=(q,))
    pr = Process(target=read, args=(q,))
    pw.start()
    pr.start()

    pw.join()
    pr.terminate()



 # ----------------------------------------
    # mtc = MongoDBTaskClient()
    # while True:
    #     # print('Process to write: %s' % os.getpid())
    #     time.sleep(2)
    #     tasks = mtc.get_task()
    #     print 'Queue is empty:--', q.empty()
    #     print 'Queue qsize:--', q.qsize()
    #     print 'Tasks count:--',tasks.count()
    #
    #     # 如果队列为空，则取tasks.linit(3)
    #     # 如果队不为空，判断q.qsize()是否小于3,小于3,则取tasks.linmit(3-q.qsize())添加到q.
    #     # 如果tasks.count()为0,则循环等待。。
    #     if q.empty():
    #         if tasks.count() > n:
    #             tasks = tasks.limit(n)
    #     else:
    #         if q.qsize() < n:
    #             tasks = tasks.limit(n-q.qsize())
    #     for t in tasks:
    #         print '22222'
    #         app_name = t['app_name']
    #         q.put(app_name)
    #     # time.sleep(2)
    #     print '3333'
    #
    #     g = gevent.spawn(read, q)
    #     g.join()




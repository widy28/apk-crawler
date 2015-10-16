#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from channels.pywget import wget
import hashlib, os, sys
reload(sys)
sys.setdefaultencoding('utf8')
import re
from channels.settings import APK_IMAGE_DIR, APK_DOWNLOAD_DIR, CHANNELS_NAME_DICT, TOOLS_DIR, PROJECT_DIR, ERR_TYPES

from channels.items import ChannelsItem
from scrapy.selector import Selector
from scrapy.http import Request
import random
from pymongo import MongoClient
from channels import settings
from scrapy import log
import datetime

def log_page(response, filename):
    with open(os.path.sep.join(['debug', filename]), 'w') as f:
        try:
            f.write("%s\n%s\n%s\n" % (response.url, response.headers, response.body))
        except:
            f.write("%s\n%s\n" % (response.url, response.headers))


def get_search_list(response, url_list_xpath, name_list_xpath, func, host):

    # apk_name = response.meta['apk_name'].decode('utf8')
    apk_name = response.meta['apk_name']
    app_channel = response.meta['app_channel']

    html = Selector(response)
    search_url_list = html.xpath(url_list_xpath).extract()
    search_name_list = html.xpath(name_list_xpath).extract()

    print search_name_list
    print search_url_list,'++++'

    if host == 'http://apk.gfan.com':
        # 特殊处理----去掉空格
        search_name_list = [n.strip() for n in search_name_list]

    if host == 'http://down.tech.sina.com.cn':
        # todo----编码特殊处理，去掉空格,换行符，
        # 比如搜索招商银行，但是新浪网站的应用名为 招商银行手机银行，就会造成匹配不上无法下载
        search_name_list = [n.strip().split(' ')[0] for n in search_name_list]

    if 'eoemarket.com' in host:
        search_url_list = [url.strip() for url in search_url_list]

    if 'meizumi.com' in host:
        search_name_list = [n.replace('...', '') for n in search_name_list]

    if 'zol.com.cn' in response.url:
        # 特殊处理
        # 将高亮的apk_name 拼接到 search_name_list 的每个元素。
        search_name_list = [apk_name+n for n in search_name_list]

    if 's.paopaoche.net' in response.url:
        # 特殊处理
        # search_name_list的个数是search_url_list的元素个数的2倍，如招商银行手机客户端下载|招商银行下载 v3.1.1 - 跑跑车安卓网
        if len(search_name_list)/len(search_url_list) == 2:
            new_name_list = zip(search_name_list[::2], search_name_list[1::2])
            search_name_list = [apk_name if apk_name in tn else '' for tn in new_name_list]

    headers = {
        # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        # 'Accept-Encoding': 'gzip, deflate, sdch',
        # 'Cache-Control': 'no-cache',
        # 'Accept-Language': 'zh-CN,zh;q=0.8',
        # 'Connection': 'keep-alive',
        # 'Host': 'www.mumayi.com',
        # 'Referer': 'http://dl.pconline.com.cn/download/86771.html',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36'
    }


    if apk_name in search_name_list:
        """
        # 完全匹配应用名方式
        """
        print '1----'*10
        print response.meta
        detail_url = host + search_url_list[search_name_list.index(apk_name)]
        return Request(detail_url, meta=response.meta, callback=func, headers=headers)
    elif filter(lambda name: apk_name in name, search_name_list):
        """
        # 部分匹配应用名方式：满足 apk_name是列表search_name_list中每个元素的 子字符串 就下载。。
        """
        print '2---'*10
        print search_name_list
        new_search_name_list = filter(lambda name: apk_name in name, search_name_list)
        url_list = []
        print new_search_name_list, '3'*10

        for n in new_search_name_list:
            print '5---'*10
            detail_url = host + search_url_list[search_name_list.index(n)]

            # 注意，此时meta的参数需要改为当前网站应用的应用名，而不是之前搜索的apk_name
            url_list.append(Request(detail_url, meta={'apk_name': apk_name,
                                                      'app_name': n,
                                                      'app_channel': app_channel},
                                    callback=func, headers=headers))

        return url_list
    # search_url_list，则下载所有的搜索结果。
    elif search_url_list and len(search_name_list) > len(search_url_list):
        url_list = []
        for u in search_url_list:
            print '6----'*10
            detail_url = host + u
            url_list.append(Request(detail_url, meta={'apk_name': apk_name, 'app_channel': app_channel}, callback=func, headers=headers))
        return url_list
    else:
        print '7---'*10
        return None




def download(**params_dic):

    """
        params_dic = {} # 参数字典
        params_dic['app_channel'] = app_channel     # 渠道
        params_dic['app_link'] = app_link           # apk下载链接
        params_dic['save_dir'] = save_dir           # 下载apk保存的目录
        params_dic['app_name'] = app_name           # 要下载的apk的应用名称
        params_dic['app_pn'] = app_pn               # apk包名
        params_dic['app_version'] = app_version     # apk版本号
        params_dic['app_size'] = app_size           # apk文件的大小
        params_dic['app_detail_url'] = app_detail_url  # apk下载页面的url
        params_dic['app_download_times'] = app_download_times  # apk的下载次数
    """
    app_channel = params_dic['app_channel']
    app_link = params_dic['app_link']
    save_dir = params_dic['save_dir']
    app_name = params_dic['app_name']
    app_version = params_dic['app_version']
    app_pn = params_dic['app_pn']
    app_size = params_dic['app_size']
    app_detail_url = params_dic['app_detail_url']
    app_download_times = params_dic['app_download_times']

    def downloadPercent(blocknum, blocksize, totalsize):
            '''回调函数
            @blocknum: 已经下载的数据块
            @blocksize: 数据块的大小
            @totalsize: 远程文件的大小
            '''
            percent = 100.0 * blocknum * blocksize / totalsize
            if percent > 100:
                percent = 100
            # print '%d '%percent +'% \r'
            sys.stdout.write("%.2f%%"% percent + '\r')
        # import socket
        # socket.setdefaulttimeout(3)

    """
    下载文件完成之后再入库，未下载完成，无法获得md5，签名等信息入库，会造成信息不同步。
    """
    try:
        # 生成一个随机5位数，用于防止包名，版本号都不存在的情况下的文件名重复。
        rs = str(random.random())  # 用于生成一个0到1的随机符点数: 0 <= n < 1.0
        app_filename = '_'.join((app_pn, app_version, rs))+'.apk'
        save_file = os.path.sep.join([save_dir, app_filename])
        # 下载开始
        # urllib.urlretrieve(app_link, save_file, downloadPercent)

        print '%s download start:'%app_name

        # 生成模拟的浏览器
        # 发送的头部信息
        headers = {
            # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            # 'Accept-Encoding': 'gzip, deflate, sdch',
            # 'Cache-Control': 'no-cache',
            # 'Accept-Language': 'zh-CN,zh;q=0.8',
            # 'Connection': 'keep-alive',
            # 'Host': 'www.mumayi.com',
            # 'Referer': 'http://dl.pconline.com.cn/download/86771.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36'
        }
        if not os.path.isdir(save_dir):
            os.makedirs(save_dir)
        try:
            wget().download(app_link, save_file, headers)
        except:
            ## 下载失败。
            add_error_app_info(app_channel, app_name, '1')
            yield None
        print '%s download end.'%app_name

        # # 代理IP地址，防止自己的IP被封禁
        # proxyURL = 'http://120.193.146.96:842'
        # #设置代理
        # proxy = urllib2.ProxyHandler({'http': proxyURL})
        # # 设置cookie
        # cookie = cookielib.LWPCookieJar()
        # # 设置cookie处理器
        # cookieHandler = urllib2.HTTPCookieProcessor(cookie)
        # # 设置登录时用到的opener，它的open方法相当于urllib2.urlopen
        # opener = urllib2.build_opener(cookieHandler)
        #
        #
        # request = urllib2.Request(url='http://apps.wandoujia.com/apps/com.ecitic.bank.mobile/download',headers=headers)
        # response = urllib2.urlopen(request)
        # # 获取其中的内容
        # content = response.read()
        # print '--------------------------'
        # with open(save_file, "wb") as code:
        #      code.write(content)
        # print '=========================='
        # #获取状态吗
        # status = response.getcode()
        # print status, '-------------------'


        # 抽取图标
        print '%s get image start:'%app_name
        try:
            print os.path.sep.join(['.', TOOLS_DIR, 'aapt'])+' dump badging '+save_file
            app_info = os.popen(os.path.sep.join(['.', TOOLS_DIR, 'aapt'])+' dump badging '+save_file).read()
        except:
            ## 解析失败。
            add_error_app_info(app_channel, app_name, '2')
            yield None

        # 获取apk真正的名称app_name
        """ application-label:'CMB'
            application-label-zh_CN:'招商银行'
        """
        # 如果没有application-label-zh_CN 则去查找application-label。
        pattern = re.compile("application-label-zh_CN:'(.*?)'")
        re_info = re.search(pattern, app_info)
        try:
            info = re_info.group()
            app_name = info.split("'")[1]
        except:
            pattern = re.compile("application-label:'(.*?)'")
            re_info = re.search(pattern, app_info)
            info = re_info.group()
            app_name = info.split("'")[1]

        # 如果前面页面不能直接获取到包名，则在此获取包名
        if not app_pn:
            # 获取包名
            pattern = re.compile("package: name='(.*?)'")
            re_info = re.search(pattern, app_info)
            info = re_info.group()
            app_pn = info.split("'")[1]

        if not app_version:
            pattern = re.compile("versionName='(.*?)'")
            re_info = re.search(pattern, app_info)
            info = re_info.group()
            app_version = info.split("'")[1]

        # 如果前面页面不能直接获取到文件大小
        if not app_size:
            app_size = str(os.path.getsize(os.sep.join([PROJECT_DIR, save_file])))

        # 获取apk图标
        pattern = re.compile("application: label='(.*?)' icon='(.*?)'")
        re_info = re.search(pattern, app_info)
        info = re_info.group()
        pattern1 = re.compile("icon='(.*?)'")
        png_re_info = re.search(pattern1, info)
        png_info = png_re_info.group()
        png_d = png_info.split("'")[1]
        image_save_dir = os.path.sep.join([APK_IMAGE_DIR, app_channel, '_'.join((app_pn, app_version))])
        # 判断目录是否存在，不存在则创建
        if not os.path.isdir(image_save_dir):
            os.makedirs(image_save_dir)
        # 执行解压命令 获取图标文件路径
        c = 'unzip -o -j '+save_file+' '+png_d+' -d '+image_save_dir
        p = os.popen(c).read()
        png_dir = p[p.find("extracting: ")+12:].replace('/', os.sep)  # apk的图标文件路径
        print '%s get image end.'%app_name

        print '%s get md5= start:'%app_name
        # 获取apk签名md5码和签名文件md5码
        sign_c = 'java -cp '+os.path.sep.join([TOOLS_DIR, 'wandoujia-tools.jar'])+' com.wandoujia.tools.ApkSignatureToolsMain '+save_file
        sign_info = os.popen(sign_c).read()
        sign_md5 = sign_info[13:45]
        signfile_md5 = sign_info[50:]

        # 获取apk文件的md5码
        app_MD5 = md5_file(save_file)
        print '%s get image end.'%app_name

        # 遍历save_dir下的所有文件，查询是否存在app_MD5值的文件
        # 存在则删除当前文件，不进行重命名，直接入库。
        # 不存在则进行文件重命名，文件保留
        # current_dir:当前路径
        # child_dirs:子文件夹
        # files:当前目录下的所有文件列表
        for current_dir, child_dirs, files in os.walk(os.sep.join([PROJECT_DIR, save_dir])):

            # 先将当前下载完成的文件名在files里删除
            files.remove(app_filename)

            def equal(f):
                f = os.sep.join([current_dir, f])
                return app_MD5 == md5_file(f)

            result = filter(equal, files)
            print result, '*&*&*&*&*&'*5
            if result:
                # 说明有相同md5的文件存在，则把当前现在的文件进行删除
                os.system('rm ' + os.sep.join([current_dir, app_filename]))
                save_file = os.path.sep.join([save_dir, result[0]])
            else:
                # 没有相同md5的文件存在，则进行重命名
                ## 对文件重命名
                rename_filename = '_'.join((app_pn, app_version, app_MD5))+'.apk'
                rename_save_file = os.path.sep.join([save_dir, rename_filename])
                # 判断 rename_save_file 该名字的文件是否存在
                if not os.path.exists(os.sep.join([PROJECT_DIR, rename_save_file])):
                    # 将apk文件名修改为 包名_版本号
                    # 重命名文件：linux命令 mv a.apk b.apk   windows命令 rename a.apk b.apk
                    # windows 重命名文件命令
                    # os.system('rename ' + save_file + ' ' + rename_filename)
                    # # linux 重命名文件命令
                    os.system('mv ' + save_file + ' ' + rename_save_file)
                    save_file = rename_save_file
        print save_file,'$#$#$#$#$#$#--'*5


        item = ChannelsItem()
        item['app_channel'] = CHANNELS_NAME_DICT.get(app_channel)
        item['app_name'] = app_name
        item['app_pn'] = app_pn
        item['app_link'] = app_link
        item['app_version'] = app_version
        item['app_size'] = app_size
        item['app_signMD5'] = sign_md5
        item['app_signFileMD5'] = signfile_md5   # 此字段作废，其实是与app_MD5是同一值
        item['app_MD5'] = app_MD5
        item['app_icon'] = png_dir
        item['app_file'] = save_file
        item['app_detail_url'] = app_detail_url
        item['app_download_times'] = app_download_times

        print item

        yield item
    except:
        raise
        print 'error------'
        yield None

def md5_str(str):
    m = hashlib.md5()
    m.update(str)
    return m.hexdigest()

def md5_file(save_file):
    md5file = open(save_file, 'rb')
    md5 = hashlib.md5(md5file.read()).hexdigest()
    md5file.close()
    return md5

def get_mongo_collection(collection):
    mongoclient = MongoClient(
            settings.MONGODB_SERVER,
            settings.MONGODB_PORT
        )
    db = mongoclient[settings.MONGODB_DB]
    collection = db[collection]
    return collection

def add_error_app_info(app_channel, app_name, err_type):
    insert_dic = {}
    app_name = app_name.encode('utf8')
    insert_dic['app_name'] = app_name
    insert_dic['app_channel'] = app_channel
    insert_dic['err_type'] = err_type
    insert_dic['err_time'] = get_now_time()
    try:
        collection = get_mongo_collection(settings.MONGODB_COLLECTION_ERROR)
        collection.insert(insert_dic)
        log.msg("error_app_info(%s--%s--%s) added to MongoDB database success."%(app_channel, app_name, ERR_TYPES[err_type]),
                level=log.DEBUG)
    except:
        log.msg("error_app_info(%s--%s--%s) added to MongoDB database unsuccess!!!!"%(app_channel, app_name, ERR_TYPES[err_type]),
                level=log.DEBUG)

def get_now_time():
    now = datetime.datetime.now()
    return now.strftime('%Y-%m-%d %H:%M:%S %f')


def createMongodbClient(collection):
    client = MongoClient(
            settings.MONGODB_SERVER,
            settings.MONGODB_PORT
    )
    db = client[settings.MONGODB_DB]
    if settings.MONGODB_DB_USERNAME and settings.MONGODB_DB_PWD:
        db.authenticate(settings.MONGODB_DB_USERNAME, settings.MONGODB_DB_PWD)
    collection = db[collection]
    return collection
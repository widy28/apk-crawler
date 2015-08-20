#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from scrapy.exceptions import IgnoreRequest
from twisted.internet import utils
from twisted.internet import defer, reactor
from scrapy.http import HtmlResponse, Request, Response
from scrapy.contrib.downloadermiddleware.redirect import RedirectMiddleware
from time import time
import os

class AllowPhantomjsMiddlewares(object):
    def process_request(self, request, spider):
        allow_middleware_url = ['dl.pconline.com.cn', 'paopaoche.net/android',
                                'android.d.cn/software', 'www.pc6.com']

        if filter(lambda u: u in request.url, allow_middleware_url):
            print '111111111111'
            htmldoc = os.popen('phantomjs scrapyweb.js %s'%request.url).read()
            # with open(os.path.sep.join(['debug', 'get_222222.html']), 'w') as f:
            #     f.write("%s" %htmldoc)
            return HtmlResponse(request.url, body=htmldoc, request=request)
        else:
            print '22222222222'
            return None
    # def process_response(self, request, response, spider):

        # # print request.meta['apk_name'],'================='
        # # print request.meta.get('list', '')
        # # print '0000000000000000000000'
        # if len(response.body) == 5000:
        #     # print '111111111111'
        #     raise IgnoreRequest("body length > 5000")
        # else:
        #     return response

    # def process_exception(self, request, exception, spider):
    #     print '10101010101010'*10
    #     return exception
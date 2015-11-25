#!/usr/lib/phantomjs
// todo linux or windows phantomjs's path
//#!D:\workspace\Selenium+phantomjs\phantomjs-2.0.0-windows\bin\phantomjs.exe

var page = require('webpage').create();

page.customHeaders = {
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Connection': 'keep-alive',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
};
page.settings.userAgent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.76 Safari/537.36';
phantom.outputEncoding = 'gbk';
var system = require('system');
page.open(system.args[1], function(status){
    console.log(system.args[1])
    if(status == 'success'){
        console.log(page.content)
    }else{
        console.log(status)
    }
    phantom.exit();
});


//if (phantom.args.length >= 1){
//        var url = phantom.args[0];
//        var timeOut = 10000;
//        if (phantom.args.length == 2){
//                timeOut = Math.min(30000, Math.max(0, phantom.args[1]));
//        }
//
//        var page = require('webpage').create();
//        page.customHeaders = {
//                'Accept-Language': 'zh-CN,zh;q=0.8',
//                'Connection': 'keep-alive',
//                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
//                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
//                'DNT': '1'
//        };
//        page.settings.userAgent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.76 Safari/537.36';
//        page.open(encodeURI(url),
//                        function(status){
//                                if (status != 'success'){
//                                        console.log('Err, status=' + status);
//                                        phantom.exit(1);
//                                }
//                                console.log(page.content);
//                                phantom.exit();
//                        });
//        setTimeout(function(){
//                console.log(page.content);
//                phantom.exit();
//        }, timeOut);}else {
//        console.log('Usage:');
//        console.log('\tphantomjs scrapyweb.js url timeout');
//        phantom.exit(1);}
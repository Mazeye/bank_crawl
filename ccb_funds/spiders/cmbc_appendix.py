# -*- coding: utf-8 -*-
# 民生银行
# 没有产品说明书
import scrapy
import json
import re
from ccb_funds.items import FundsInfoItem


class MsbAppendixSpider(scrapy.Spider):
    name = 'cmbc_appendix'
    allowed_domains = ['cmbc.com.cn']
    start_urls = ['http://www.cmbc.com.cn/channelApp/ajax/Financialpage']
    
    def start_requests(self):
        json_data = r'{"request":{"body":{"page":1,"row":9999},"header":{"device":{"model":"SM-N7508V","osVersion":"4.3",' \
                    r'"imei":"352203064891579","isRoot":"1","nfc":"1","brand":"samsung","mac":"B8:5A:73:94:8F:E6",' \
                    r'"uuid":"45cnqzgwplsduran7ib8fw3aa","osType":"01"},"appId":"1","net":{"ssid":"oa-wlan",' \
                    r'"netType":"WIFI_oa-wlan","cid":"17129544","lac":"41043","isp":"","ip":"195.214.145.199"},' \
                    r'"appVersion":"3.60","transId":"Financialpage","reqSeq":"0"}}}'
        json_data = json.loads(json_data)
        json_data = dict(json_data)
        # print(json_data)
        headers = {
                      'Accept': r'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                      'Accept-Encoding': 'gzip, deflate',
                      'Accept-Language': 'zh-CN,zh;q=0.9',
                      'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome'
                                    r'/68.0.3440.106 Safari/537.36',
                      'Content-Type': 'application/json;charset=UTF-8',
                      'Referer': r'https://www.baidu.com/s?ie=utf-8&f=3&rsv_bp=1&rsv_idx=1&tn=baidu&wd',
                      'Connection': r'keep-alive',
                  }
        yield scrapy.Request(
            url=self.start_urls[0],
            encoding='utf-8',
            headers=headers,
            body=json.dumps(json_data),
            method='POST',
            dont_filter = True,
            callback=self.parse)

    def parse(self, response):
        # return response
        # print('响应开始：')
        # print(response.text)
        respo = json.loads(response.text)
        datas = respo["returnData"]["list"]
        # f = open('test.txt', 'w')
        # f.write(str(datas))
        # f.close()
        for data in datas:
            item = FundsInfoItem()
            item["pid"] = data['PRD_CODE']
            item["pname"] = data['PRD_NAME']
            item["prate"] = data['NEXT_INCOME_RATE']
            item["pperiod"] = str(data['LIVE_TIME'])+u'天'
            item["pfloor"] = data['PFIRST_AMT']
            yield item

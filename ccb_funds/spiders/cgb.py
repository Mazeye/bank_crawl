# -*- coding: utf-8 -*-
# 广发银行
import scrapy
import json
import re
from ccb_funds.items import FundsInfoItem


class Cgbbank(scrapy.Spider):
    name = "cgb"
    allowed_domains = ["cgbchina.com"]
    start_urls = ['http://www.cgbchina.com.cn/Channel/16684283?nav=2','http://www.cgbchina.com.cn/Channel/21828547']
    def start_requests(self):
        for i in range(len(self.start_urls)):
            yield scrapy.FormRequest(
                url = self.start_urls[i],
                method = 'GET',
                callback=self.parse)

    def parse(self, response):
        # print "内部网页"
        # print response.body
        indatas = response.xpath('//tr[@class="bg2"]')
        # print len(indatas)
        # item = FundsInfoItem()
        # item["pid"] = "test"
        for data in indatas:
            item = FundsInfoItem()
            item["pname"] = data.xpath('normalize-space(./td[@class="name"]/a/text())').extract()[0]
        
            item["pid"] = data.xpath('./td[@class="name"]/a/@href').extract()[0].split('productno=')[-1]

            item["prate"] = data.xpath('./td')[4].xpath('./b/text()').extract()[0]
        
            item["pfloor"] = data.xpath('./td')[3].xpath('./text()').extract()[0]
        
            item["pperiod"] = data.xpath('./td')[2].xpath('normalize-space(./text())').extract()[0]
            yield item
        

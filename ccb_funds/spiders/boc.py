# -*- coding: utf-8 -*-
# 中国银行
import scrapy
import json
import re
from ccb_funds.items import FundsInfoItem
class Cibbank(scrapy.Spider):
    name = "boc"
    allowed_domains = ["boc.cn"]
    start_urls = ['http://www.boc.cn/fimarkets/cs8/201109/t20110922_1532694.html']
    def start_requests(self):
        yield scrapy.FormRequest(
            url = self.start_urls[0],
            method = 'GET',
            callback=self.parse)

    def parse(self, response):
        # print "内部网页"
        # print response.body
        indatas = response.xpath('//tbody/tr')
        
        for data in indatas:

            item = FundsInfoItem()

            item["pname"] = data.xpath('./td')[1].xpath('./text()').extract()[0]

            item["pid"] = data.xpath('./td')[0].xpath('./text()').extract()[0]

            item["prate"] = data.xpath('./td')[3].xpath('./text()').extract()[0]
        
            item["pfloor"] = data.xpath('./td')[4].xpath('./text()').extract()[0]
        
            item["pperiod"] = data.xpath('./td')[2].xpath('./text()').extract()[0]
            yield item
        

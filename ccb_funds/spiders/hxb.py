# -*- coding: utf-8 -*-
# 华夏银行
import scrapy
import json
import re
from ccb_funds.items import FundsInfoItem
class Hxbank(scrapy.Spider):
    name = "hxb"
    allowed_domains = ["hxb.com"]
    start_urls = ['http://www.hxb.com.cn/grjr/lylc/zzfsdlccpxx/index.shtml']


    def parse(self, response):
        # print "打印response"
        datas = response.xpath('//ol/li[@name="pageli"]')
        # print len(datas)
        # print datas[0].xpath('./div/p/a/text()').extract()[0].encode("utf-8")
        # print datas[0].xpath('normalize-space(./div/div[@class="box_lf"]/p[@class="box_num"]/text())').extract()[0]
        # print datas[0].xpath('./div/ul/li/span[@class="amt"]/text()').extract()[0].encode("utf-8")+'万'
        # print datas[0].xpath('normalize-space(./div/ul/li/span[@class="highlight"]/text())').extract()[0].encode("utf-8")

        for data in datas:
            item = FundsInfoItem()
            # item["pid"] = 
            item["pname"] = data.xpath('./div/p/a/text()').extract()[0]
            item["prate"] = data.xpath('normalize-space(./div/div[@class="box_lf"]/p[@class="box_num"]/text())').extract()[0]
            item["pperiod"] = data.xpath('normalize-space(./div/ul/li/span[@class="highlight"]/text())').extract()[0]
            item["pfloor"] = data.xpath('./div/ul/li/span[@class="amt"]/text()').extract()[0]+'0000'
            yield item
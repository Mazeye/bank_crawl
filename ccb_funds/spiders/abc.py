# -*- coding: utf-8 -*-
# 农业银行
import scrapy
import json
import re
from ccb_funds.items import FundsInfoItem

class Pinganbank(scrapy.Spider):
    name = "abc"
    allowed_domains = ["abchina.com"]
    start_urls = ['http://ewealth.abchina.com/app/data/api/DataService/BoeProductV2?s=20&o=0&w=%25E5%258F%25AF%25E5%2594%25AE%257C%257C%257C%257C%257C%257C%257C1%257C%257C0%257C%257C0&i=',\
    'http://ewealth.abchina.com/fs']
    def start_requests(self):
        for i in range(1,7):
            yield scrapy.FormRequest(
                url = self.start_urls[0]+str(i),
                method = 'GET',
                callback=self.parse)

    def parse(self, response):
        # print "打印response"
        datas=response.xpath('//Table')
        # print len(datas)
        for data in datas:
            item = FundsInfoItem()
            item["pid"] = data.xpath('./ProductNo/text()').extract()[0]
            item["pname"] = data.xpath('./ProdName/text()').extract()[0]
            item["prate"] = data.xpath('./ProdProfit/text()').extract()[0]
            item["pperiod"] = data.xpath('./ProdLimit/text()').extract()[0]
            item["pfloor"] = data.xpath('./PurStarAmo/text()').extract()[0]
            yield item
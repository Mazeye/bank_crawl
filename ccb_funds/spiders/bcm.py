# -*- coding: utf-8 -*-
# 交通银行
import scrapy
import json
import re
from ccb_funds.items import FundsInfoItem

class Bcmbank(scrapy.Spider):
    name = "bcm"
    allowed_domains = ["bankcomm.com"]
    start_urls = ['http://www.bankcomm.com/BankCommSite/jyjr/cn/lcpd/queryFundInfoListNew.do']
    def start_requests(self):
        yield scrapy.FormRequest(
            url = self.start_urls[0],
            method = 'GET',
            callback=self.parse1)

    def parse1(self, response):
        # print "打印response"
        datas = response.xpath('//div[@class="fundsList"]/ul[@class="lc-item-list"]')
        # print len(datas[0].xpath('./li'))
        for data_list in datas:
            for data in data_list.xpath('./li'):
                base = 'http://www.bankcomm.com//BankCommSite/jyjr/cn/lcpd/queryFundInfoNew.do?code='
                url = base+data.xpath('./div[@class="right-box"]/a/@href').extract()[0].split('&code=')[-1]
                yield scrapy.Request(url=url,method = 'GET',callback=self.parsein)
    def parsein(self, response):
        # print "内部网页"
        indatas = response.xpath('//tr')
        item = FundsInfoItem()
        for data in indatas:
            if u'产品名称' in data.xpath('./th/text()').extract()[0]:
                # print "产品名称"
                item["pname"] = data.xpath('normalize-space(./td/text())').extract()[0]
            if u'产品代码' in data.xpath('./th/text()').extract()[0]:
                # print "产品代码"
                item["pid"] = data.xpath('normalize-space(./td/text())').extract()[0]
            if u'预计年化收益率' in data.xpath('./th/text()').extract()[0]:
                # print "预计年化收益率"
                item["prate"] = data.xpath('normalize-space(./td/text())').extract()[0]
            if u'起点金额' in data.xpath('./th/text()').extract()[0]:
                # print "起点金额"
                item["pfloor"] = data.xpath('normalize-space(./td/text())').extract()[0]
            if u'投资期限' in data.xpath('./th/text()').extract()[0]:
                # print "投资期限"
                item["pperiod"] = data.xpath('normalize-space(./td/text())').extract()[0]
        yield item

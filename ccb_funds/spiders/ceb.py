# -*- coding: utf-8 -*-
# 光大银行
import scrapy
import json
import re
from ccb_funds.items import FundsInfoItem
import time

class Cebcbank(scrapy.Spider):
    name = "ceb"
    allowed_domains = ["cebbank.com"]
    start_urls = ['http://www.cebbank.com/eportal/ui?moduleId=12073&struts.portlet.action=/app/yglcAction!listProduct.action',\
    'http://www.cebbank.com/site/ygyyt/7990166/index.html',\
    'http://www.cebbank.com/site/gryw/grck/66885778/acbcp/c8c30d44-']

    def start_requests(self):
        # 抓取新客理财
        yield scrapy.FormRequest(url=self.start_urls[1], method='GET', callback=self.parsexk)
        # 抓取安存宝
        for j in range(1,15):
            acburl = self.start_urls[2]+str(j)+'.html'
            yield scrapy.FormRequest(url=acburl, method='GET', callback=self.parseacb)
        
        # 抓取理财产品
        TZBZMC_flag = ['','RMB']
        for flag in TZBZMC_flag:
            for i in range(1,20):
                curpage = i
                yield scrapy.FormRequest(
                    url = self.start_urls[0],
                    formdata={
                            'channelIds[]': ['yxl94','ygelc79','hqb30','dhb2','cjh','gylc70','Ajh67','Ajh84','901776','Bjh91',
                            'Ejh99','Tjh70','tcjh96','ts43','ygjylhzhMOM25','yxyg87','zcpzjh64','wjyh1','smjjb9',
                            'ty90','tx16','ghjx6','wf36','ygxgt59','wbtcjh3','wbBjh77','wbTjh28','sycfxl','cfTjh',
                            'jgdhb','tydhb','jgxck','jgyxl','tyyxl','dgBTAcp','27637097','27637101','27637105',
                            '27637109','27637113','27637117','27637121','27637125','27637129','27637133',
                            'gyxj32','yghxl','ygcxl','ygjxl','ygbxl','ygqxl','yglxl','ygzxl'],
                'codeOrName': '',
                'TZBZMC': flag,
                'QGJE': '',
                'QGJELEFT': '',
                'QGJERIGHT': '',
                'CATEGORY': '',
                'CPQXLEFT': '',
                'CPQXRIGHT': '',
                'CPFXDJ': '',
                'SFZS': 'Y',
                'qxrUp': 'Y',
                'qxrDown': '',
                'dqrUp': '',
                'dqrDown': '',
                'qdjeUp': '',
                'qdjeDown': '',
                'qxUp': '',
                'qxDown': '',
                'yqnhsylUp': '',
                'yqnhsylDown': '',
                'page': str(i),
                "pageSize": "5"},
                    method = 'POST',
                    callback=self.parse5)
    # IF pageSize=5
    def parse5(self, response):
        # print "打印response"
        # print len(response.xpath('//div[@class="lccp_main_content_tx"]/ul/li'))
        # datas = response.xpath('//div[@class="lccp_main_content_tx"]/ul/li')
        datas = response.xpath('//div[@class="lccp_main_content_lb"]/table/tbody/tr')
        # print len(datas)
        for data in datas[1:]:
            item = FundsInfoItem()
            temp = data.xpath('./td')
            # print len(temp)
            item["pid"] = temp[0].xpath('./a/@data-analytics-click').extract()[0].split('-')[-1]
            item["pname"] = temp[0].xpath('normalize-space(./a/text())').extract()[0]
            item["prate"] = temp[5].xpath('normalize-space(./div/span/text())').extract()[0]
            item["pperiod"] =temp[4].xpath('normalize-space(./text())').extract()[0]
            item["pfloor"] = temp[3].xpath('normalize-space(./text())').extract()[0]
            yield item
    
    def parsexk(self,response):
        print("新客理财爬取")
        xklc = response.xpath('//div[@class="xklc_con"]')
        print(len(xklc))
        for product in xklc:
            item = FundsInfoItem()
            item["pid"] =  product.xpath('./div/div/div[@class="xklc_cptab"]/ul[@class="tb2 fl"]/li')[0].xpath('normalize-space(string(.))').extract()[0]
            item["pname"] = product.xpath('./div/div/div[@class="xklc_title"]/text()').extract()[0]
            try:
                item["prate"] = product.xpath('./div/div/div[@class="xklc_sz"]/div')[0].xpath('normalize-space(string(.))').extract()[0]
            except:pass
            try:
                item["pperiod"] = product.xpath('./div/div/div[@class="xklc_cptab"]/ul[@class="tb2 fl"]')[1].xpath('./li')[1].xpath('normalize-space(string(.))').extract()[0]
            except:pass
            try:
                item["pfloor"] = product.xpath('./div/div/div[@class="xklc_cptab"]/ul[@class="tb2 fl"]')[1].xpath('./li')[0].xpath('normalize-space(string(.))').extract()[0]
            except:pass
            yield item
    def now(self):
        return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))   
    def parseacb(self,response):
        print("抓取安存宝")
        products = response.xpath('//tr[@class="acb_table"]')
        print(len(products))
        for pro in products:
            procon = pro.xpath('./td')
            endtime = procon[2].xpath('./span')[1].xpath('string(.)').extract()[0]
            if self.now()<endtime:
                print(endtime,"未过期")
                item = FundsInfoItem()
                item["pname"] = procon[0].xpath('./a/@title').extract()[0]
                # item["pid"] 
                item["prate"] = procon[5].xpath('string(.)').extract()[0]
                item["pperiod"] = procon[4].xpath('string(.)').extract()[0]
                item["pfloor"] = procon[3].xpath('string(.)').extract()[0]+procon[1].xpath('string(.)').extract()[0]
                yield item
            else:
                print(endtime,"已过期")

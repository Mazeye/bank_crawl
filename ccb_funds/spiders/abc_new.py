# -*- coding: utf-8 -*-
# 农业银行
import scrapy
import json
import re
from ccb_funds.items import FundsInfoItem
import pdfplumber
import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")
# sys_encoding = sys.getfilesystemencoding()
class Pinganbank(scrapy.Spider):
    name = "abc_new"
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
            productUrl = self.start_urls[1]+'/'+str(item["pid"])+'.htm'
            # yield item
            yield scrapy.FormRequest(url=productUrl,method='GET',meta={"item":item},callback=self.parse_pdf)
    
    def parse_pdf(self,response):
        # print response
        item = response.meta['item']
        print(item)
        print("产品详情")
        subUrl = response.xpath('//tr/td/a/@href').extract()[0].strip('.')
        pdfUrl= self.start_urls[1]+subUrl
        print(pdfUrl)
        yield scrapy.FormRequest(url=pdfUrl,method='GET',meta={"item":item},callback=self.get_scale)

    def get_scale(self,response):
        item = response.meta['item']
        filename = 'pdf/'+response.url.split('/')[-1]
        f = open(filename,'wb')
        f.write(response.body)
        f.close()
        pdf = pdfplumber.open(filename)
        item["pscale"] = self.getScale(pdf)
        yield item

    def printcn(self,msg):
       print(msg.decode('utf-8').encode(sys_encoding))

    def getScale(self,pdf):
        p0 = pdf.pages[1:3]#注意此处的pages是一个列表，索引是从0开始的
        for i in range(len(p0)):
            table = p0[i].extract_tables()
            for item in table:
                for subitem in item:
                    if u'产品认购规模' in subitem:
                        print("found")
                        p=subitem.index(u'产品认购规模')
                        self.printcn(subitem[p+1])
                        return "".join(subitem[p+1].split())
                    else:
                        print("not found")
        return "not found"

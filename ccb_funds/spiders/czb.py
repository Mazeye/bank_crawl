# -*- coding: utf-8 -*-
# 浙商银行
# 完成
import scrapy
import re
from ccb_funds.items import FundsInfoItem
import pdfplumber
import pandas as pd

class czbSpider(scrapy.Spider):
    name = 'czb'
    allowed_domains = ['czbank.com']
    start_urls = ['http://www.czbank.com/cn/personal/investment/issue/201608/t20160823_3537.shtml']


    def start_requests(self):
        yield scrapy.FormRequest(
            url = self.start_urls[0],
            method = 'GET',
            callback=self.parse_links)

    def parse(self, response):
        page = response.text
        reg = r'(永乐\d号[^<]*).*(\w\w\d\d\d\d).*(\d\.\d\d%).*起点金额(.*)[\S]上限'.decode('utf-8')
        reg = re.compile(reg)
        finfos = reg.findall(page)
        for data in finfos:
            item = FundsInfoItem()
            item["pid"] = data[1]
            item["pname"] = data[0]
            item["prate"] = data[2]
            item["pperiod"] = u'未找到投资期限'
            item["pfloor"] = data[3]
            yield item

    def parse_links(self,response):
        links = response.xpath('//font/a')
        # print len(links)
        # print links[0]
        base = 'http://www.czbank.com/cn/personal/investment/issue/201608/'
        for link in links:
            self.name = link.xpath('@oldsrc').extract()[0]
            url = base + self.name
            # print url
            yield scrapy.Request(url=url,method = 'GET',callback=self.parse_pdf)

    def parse_pdf(self,response):
        print(response.url)
        filename = 'pdf/'+response.url.split('/')[-1]
        f = open(filename,'wb')
        f.write(response.body)
        f.close()
        
        pdf = pdfplumber.open(filename)

        p0 = pdf.pages[0]#注意此处的pages是一个列表，索引是从0开始的

        table = p0.extract_table()

        item = FundsInfoItem()
        item["pid"] = "".join(table[2][1].split())
        item["pname"] = table[1][1]
        item["prate"] = table[11][1]
        item["pperiod"] = table[10][1]
        item["pfloor"] = "".join(table[5][1].split())
        item['pscale'] = "".join(table[4][1].split())
        yield item

        # df = pd.DataFrame(table)
        # output = 'csv/'+response.url.split('/')[-1].split('.')[0]
        # df.to_csv(output,encoding='utf-8')


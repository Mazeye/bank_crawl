# -*- coding: utf-8 -*-
# 恒丰银行
import scrapy
import re
from ccb_funds.items import FundsInfoItem


class hfbSpider(scrapy.Spider):
    name = 'hfbank'
    allowed_domains = ['hfbank.com.cn']
    start_urls = ['http://www.hfbank.com.cn/ucms/hfyh/jsp/gryw/lc_lb.jsp']
    
    def start_requests(self):
        yield scrapy.FormRequest(
                url = self.start_urls[0],
                formdata={'CurrType': '156,250,256,344,392,826,840,954,',
                          'limit': '0-90,90-180,180-365,365-,',
                          'nameValue': 'RsgStrtDt',
                          'pagecount': '10000',
                          'pageStartCount': '0',
                          'order': 'false',
                          'ptType': 'lcpt',
                          'search': '',
                          'Status': '01',
                          'TypeNo': '0,2,1',
                          'RiskLevel': '1,2,3,4,5,0'},
                method = 'POST',
                callback=self.parse)


    def parse(self ,response):
        reg = r'ft">(.*)<span>(.*)</span>[\s\S]{1,1000}value="(.*)"\sna[\s\S]{1,2900}font"[^<>]*>([^<>]*)</span>[\s\S]' \
              r'{1,2900}<td class="bot"><span class="font" >(.*)</span><span class="grey">(.*)</span></td>'
        reg = re.compile(reg)
        funds_info = reg.findall(response.text)
        print(funds_info)
        print(len(funds_info))
        for data in funds_info:
            item = FundsInfoItem()
            item["pid"] = data[1]
            item["pname"] = data[0]
            item["prate"] = data[2]
            item["pperiod"] = data[3]
            item["pfloor"] = data[4]+data[5]
            yield item

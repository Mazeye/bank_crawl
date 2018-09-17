# -*- coding: utf-8 -*-
# 工商银行
import scrapy
import json
import re
from ccb_funds.items import FundsInfoItem
class Cibbank(scrapy.Spider):
    name = "icbc"
    allowed_domains = ["icbc.com"]
    start_urls = ['https://mybank.icbc.com.cn/servlet/ICBCBaseReqServletNoSession?dse_operationName=per_FinanceCurProListP3NSOp&useFinanceSolrFlag=1&orderclick=0&menuLabel=11|ALL&pageFlag_turn=2&Area_code=4000&nowPageNum_turn=']
    def start_requests(self):
        headers = {
                'Accept': r'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome'
                            r'/68.0.3440.106 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': r'https://mybank.icbc.com.cn/servlet/ICBCBaseReqServletNoSession?dse_operationName=per_FinanceCurProListP3NSOp&p3bank_error_backid=120103&pageFlag=0&Area_code=4000&requestChannel=302',
                'Connection': r'keep-alive',
            }
        for i in range(1,18):
            yield scrapy.FormRequest(
                url = self.start_urls[0]+str(i),
                method = 'GET',
                headers=headers,
                callback=self.parse)

    def parse(self, response):
        # print "内部网页"
        # print response.body
        indatas = response.xpath('//div[@class="ebdp-pc4promote-circularcontainer"]')
        print(len(indatas))
        for data in indatas:

            item = FundsInfoItem()

            item["pname"] = data.xpath('./div[@class="ebdp-pc4promote-circularcontainer-head"]/span/span/a/text()').extract()[0]
            # print item["pname"]
            item["pid"] =  data.xpath('./div[@class="ebdp-pc4promote-circularcontainer-head"]/span/span/a/@href').extract()[0].split('(')[-1].split(',')[0].strip('\'')
            temp = data.xpath('./div[@class="ebdp-pc4promote-circularcontainer-content"]/table/tbody/tr/td')
            if len(temp)==5:
            
                item["prate"] = temp[0].xpath('./div/div')[1].xpath('./text()').extract()[0]
            
                item["pfloor"] = temp[1].xpath('./div/div')[1].xpath('./b/text()').extract()[0]+temp[1].xpath('./div/div')[1].xpath('./text()').extract()[0]
                
                item["pperiod"] = temp[2].xpath('./div/div')[1].xpath('string(.)').extract()[0]
            elif len(temp)==6:
                            
                item["prate"] = temp[1].xpath('./div/div')[1].xpath('./text()').extract()[0]
            
                item["pfloor"] = temp[2].xpath('./div/div')[1].xpath('./b/text()').extract()[0]+temp[1].xpath('./div/div')[1].xpath('./text()').extract()[0]
                
                item["pperiod"] = temp[3].xpath('./div/div')[1].xpath('string(.)').extract()[0]
            yield item
        

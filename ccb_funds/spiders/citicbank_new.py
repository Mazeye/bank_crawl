# -*- coding: utf-8 -*-
# 中信银行
# 结果缺失
import scrapy
import json
import re
from ccb_funds.items import FundsInfoItem
from scrapy.http import Request

class Citicbank(scrapy.Spider):
    name = "citicbank_new"
    allowed_domains = ["citicbank.com"]
    start_urls = ['https://etrade.citicbank.com/portalweb/fd/getFinaList.htm']
    i = 0
    def start_requests(self):
        for i in range(1,6):
            curpage = i
            yield scrapy.FormRequest(
                url = self.start_urls[0],
                formdata={'branchId':'701100','totuseAmt':'02','orderField':'ppo_incomerate','orderType':'desc','currentPage':str(curpage),'pageSize':'100','pwdControlFlag':'0','responseFormat':'JSON','random':'7470'},
                method = 'POST',
                callback=self.parse)

    def parse(self, response):
        # print "打印response"
        # print response.body
        datas = json.loads(response.body)['content']['resultList']
        # print datas[0]
        for data in datas:
            item = FundsInfoItem()
            item["pid"] = data['prdNo']
            item["pname"] = data['prdName']
            item["prate"] = data['incomerate']
            item["pperiod"] = data['dayDeadLine']
            item["pfloor"] = data['firstAmt']
            pdfUrl = 'https://etrade.citicbank.com/portalweb/findoc/'+str(item["pid"])+'00.html'
            item["pscale"] = pdfUrl
            # self.i = self.i+1
            # print self.i
            # yield item
            try:
                subResponse= Request(url=pdfUrl,method='GET',meta={"item":item},callback=self.get_scale,errback=self.errors)
                yield subResponse
            except:
                yield item
 
    def get_scale(self,response):
        # print "产品说明书部分"
        itemnew = response.meta['item']
        datas = response.xpath('//tr')
        for data in datas:
            datatd = data.xpath('./td')
            if len(datatd)>1:
                try:
                    name = datatd[0].xpath('string(.)').extract()[0]
                    if u'计划募集金额' in name or u'计划募集' in name or u'产品规模' in name or u'募集规模' in name or u'规模' in name:
                        result=datatd[1].xpath('string(.)').extract()[0].strip()
                        itemnew["pscale"] = result
                except:continue
        yield itemnew

    def errors(self,failure):
        print(failure)
        # item = failure.meta['item']
        # yield item

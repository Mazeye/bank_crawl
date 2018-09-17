# -*- coding: utf-8 -*-
# 平安银行
import scrapy
import json
import re
from ccb_funds.items import FundsInfoItem
class Pinganbank(scrapy.Spider):
    name = "pingan"
    allowed_domains = ["pingan.com"]
    start_urls = ['https://bank.pingan.com.cn/rmb/bron/ibank/cust/bron-ibank-pd/pc/finance/getRecommendList.do?channelCode=C0002&moduleCode=C0002_FINA_HQ_INDEX&access_source=PC',\
    'https://bank.pingan.com.cn/rmb/bron/ibank/cust/bron-ibank-pd/compFinancial/getList.do?sortBy=&sortRule=&prdTag=&privateTag=&breakEven=&prdStatus=&bottomMinInvestAmount=&topMinInvestAmount=&minInvestTerm=&maxInvestTerm=&isRMB=&prdType=&pageSize=10&access_source=PC']
    
    def start_requests(self):
        yield scrapy.FormRequest(
            url = self.start_urls[0],
            method = 'GET',
            callback=self.parsehq)
        for i in range(1,10):
            curpage = i
            yield scrapy.FormRequest(
                url = self.start_urls[1]+'&pageNum='+str(curpage),
                method = 'GET',
                callback=self.parsedq)

    def parsehq(self, response):
        # print "打印response"
        datas = json.loads(response.body.decode('utf-8'))["data"]["recommendAreas"]
        # print len(datas[0]["recommendProducts"])
        for data_list in datas:
            for data in data_list["recommendProducts"]:
                item = FundsInfoItem()
                item["pid"] = data["prdCode"]+","
                item["pname"] = data["recommendName"]
                item["prate"] = data["newIndexContent"]
                item["pperiod"] = data["recommendType"]
                if "finaSaleStatusInfo" in data["product"].keys():
                    item["pfloor"] = data["product"]["finaSaleStatusInfo"]["minAmount"]
                elif "fundSaleStatusInfo" in data["product"].keys():
                    item["pfloor"] = data["product"]["fundSaleStatusInfo"]["pfirstAmt"]
                yield item

    def parsedq(self,response):
        # print "打印response"
        datas = json.loads(response.body.decode('utf-8'))["data"]["compFinancialProducts"]
        # print len(datas)
        for data in datas:
            item = FundsInfoItem()
            if "prdCode" not in data.keys():
                data["prdCode"] = "该产品无编号"
            item["pid"] = data["prdCode"]
            item["pname"] = data["prdName"]
            item["prate"] = data["indexContent"]
            item["pperiod"] = data["investTerm"]
            item["pfloor"] = data["minInvestAmount"]
            yield item
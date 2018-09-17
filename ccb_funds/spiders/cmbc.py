# -*- coding: utf-8 -*-
# 民生银行
# 没有产品说明书
import scrapy
import json
import re
from ccb_funds.items import FundsInfoItem


class MsbSpider(scrapy.Spider):
    name = 'cmbc'
    allowed_domains = ['mszxyh.com']
    start_urls = ['https://www.mszxyh.com/peweb/DBFinancePrdList.do']
    
    def start_requests(self):
        json_data = {'pageNo': '1', 'pageSize': '10000', 'PrdState': '0'}
        # json_data = json.loads(json_data)
        # json_data = dict(json_data)
        # # print(json_data)
        headers = {
                    'Host': 'www.mszxyh.com',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Referer': 'https://www.mszxyh.com/peweb/static/dBankMain.html?pid=yhlc&CurrentPrdId=Ma'
                               'intoBankInvestBuy&PrdCode=FSAA17521X&DCChannel=MC',
                    'Content-Type': 'application/json;charset=utf-8',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Length': '40',
                    'Cookie': 'monUserKey=a2da3fd5d6b4f3c2c9f22d7718a399df; BIGipServergerenwangyin_yingyongdianzi_app_'
                              '55002_pool=1694502922.56534.0000; BIGipServerDZZH_zhixiaoyinhang-menhu_443_web_pool=253'
                              '8799114.22811.0000; JSESSIONID=m0bLkp2S9F-sTGD6IAMfChScRrpr90inhKLFdVrEuMop9Qa02K3E!-821'
                              '946643; org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=zh_CN; _PrdNoE'
                              'xit=N',
                    'Connection': 'keep-alive'
                  }
        yield scrapy.FormRequest(
            url=self.start_urls[0],
            formdata=json_data,
            method='POST',
            callback=self.parse)

    def parse(self, response):
        print('响应开始：')
        print(response.text)
        datas = json.loads(response.text)['List']
        for data in datas:
            item = FundsInfoItem()
            item["pid"] = data['PrdCode']
            item["pname"] = data['PrdName']
            item["prate"] = data['IncomeRateExt']
            # item["pperiod"] = str(data['LiveTime'])+'*'+data['UnitLiveTime']
            item["pperiod"] = str(data['LiveTime']) + '天'
            item["pfloor"] = data['PfirstAmt']
            yield item

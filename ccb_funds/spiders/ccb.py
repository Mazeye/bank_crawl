# -*- coding: utf-8 -*-
# 中国建设银行
import scrapy
import json
import re
import urllib
import pdfplumber
import pandas as pd
from ccb_funds.items import FundsInfoItem


class CcbSpider(scrapy.Spider):
    name = 'ccb'
    allowed_domains = ['ccb.com']
    start_urls = ['http://finance.ccb.com/cc_webtran/queryFinanceProdList.gsp?jsoncallback=jsonpCallback',
                  'http://finance.ccb.com/cc_webtran/queryFinanceProdDetail.gsp?']

    def start_requests(self):
        yield scrapy.FormRequest(
            url=self.start_urls[0],
            formdata={'pageNo':'1','pageSize':'100000','queryForm.saleStatus':'-1'},
            method='POST',
            callback=self.parse)

    def get_ccb_detail_rate(self, params_code):
        try:
            url = r'http://finance.ccb.com/cc_webtran/queryFinanceProdDetail.gsp?'
            headers = {
                'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
                'Referer': r'http://finance.ccb.com/cn/finance/product.html',
                'Connection': 'keep-alive'
            }
            data = {'jsoncallback':'jQuery191036942510719116894_1533864732025','params.code': params_code}
            data = urllib.parse.urlencode(data).encode('utf-8')
            req = urllib.request.Request(url, headers=headers, data=data)
            page = urllib.request.urlopen(req).read()
            page = page.decode('gbk')
            begin = re.search('jQuery191036942510719116894_1533864732025', page).end()
            page = json.loads(page[begin + 1:-1])
            page = page["pubNoticeUrl"]
            news_url = re.findall(r'@@\|.{70,130}\|@#', page)[0][3:-3]
            req2 = urllib.request.Request(news_url, headers=headers)
            page_detail = urllib.request.urlopen(req2).read()
            reg_rate = r'>(.{0,5}%)<'
            reg_rate = re.compile(reg_rate)
            last_rate = reg_rate.search(page_detail.decode('utf-8')).group(1)
            return last_rate
        except Exception as e:
            print(e)
            err_msg = 'html中无法获取到收益率'
            return err_msg

    def find_pdf(self, response):
        item = response.meta['item']
        pdf_re = re.compile(r'书\|@@\|([^"]*)"')
        try:
            pdf_url = pdf_re.search(response.text).group(1)
            if pdf_url[-3:] == 'pdf':
                yield scrapy.FormRequest(url=pdf_url, method='GET', meta={"item": item}, callback=self.parse_pdf)
            else:
                yield scrapy.FormRequest(url=pdf_url, method='GET', meta={"item": item}, callback=self.get_deep_pdf)
        except:
            item['prate'] = "未获取到产品说明书"
            yield item

    def get_deep_pdf(self, response):
        item = response.meta['item']
        pdf_url = re.search(r'href="([^"]*.pdf)"', response.text).group(1)
        pdf_url = 'http://www.ccb.com' + pdf_url
        yield scrapy.FormRequest(url=pdf_url, method='GET', meta={"item": item}, callback=self.parse_pdf)

    def parse_pdf(self, response):
        item = response.meta['item']
        f = open('temp.pdf','wb')
        f.write(response.body)
        f.close()
        pdf = pdfplumber.open('temp.pdf')
        p0 = pdf.pages
        # 注意此处的pages是一个列表，索引是从0开始的
        for i in range(len(p0)):
            table = p0[i].extract_tables()
            for line in table:
                for subline in line:
                    if u'客户预期年化收益率' in subline:
                        p = subline.index(u'客户预期年化收益率')
                        item["prate"] = subline[p + 1].replace(' ', '').replace('\r', '').replace('\n', '')
                        yield item
        item["prate"] = '产品说明书无法识别出信息，说明书参见：' + response.url
        yield item

    def parse(self, response):
        begin = re.search('jsonpCallback', response.text).end()
        datas = json.loads(response.text[begin+1:-1])['ProdList']
        for data in datas:
            item = FundsInfoItem()
            item["pid"] = data['code']
            item["pname"] = data['name']
            item["prate"] = data['yieldRate']
            item["pperiod"] = data['investPeriod']
            item["pfloor"] = data['purFloorAmt']
            # item["pscale"] = data['instructionUrl']
            if item["prate"] == 0.0:
                item["prate"] = self.get_ccb_detail_rate(item['pid'])
            if item["prate"] == 'html中无法获取到收益率':
                # 试图从子页面抓取最新收益率
                url = r'http://finance.ccb.com/cc_webtran/queryFinanceProdDetail.gsp?'
                headers = {
                    'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
                    'Referer': r'http://finance.ccb.com/cn/finance/product.html',
                    'Connection': 'keep-alive'
                }
                data = {'jsoncallback':'jQuery191036942510719116894_1533864732025','params.code': item["pid"]}
                yield scrapy.FormRequest(url=url, method='POST', headers=headers, formdata=data, meta={"item": item},
                                         callback=self.find_pdf)
            else:
                yield item

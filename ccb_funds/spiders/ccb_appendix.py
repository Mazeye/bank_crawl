# 中国建设银行
import scrapy
import urllib
from urllib import request
import pandas as pd
import re


class CcbAppendixSpider(scrapy.Spider):
    name = 'ccb_appendix'
    allowed_domains = ['ccb.com']
    start_urls = ['http://www.ccb.com/gd/cn/fhgg/']

    def start_requests(self):
        for i in range(20):
            yield scrapy.Request(
                url=self.start_urls[0] + 'fhgg_list_{}.html'.format(i),
                method='GET',
                callback=self.parse)

    def parse(self, response):
        rates_line = []
        a_list = response.xpath('//ul[@class="list"]/li/a').extract()
        for item in a_list:
            reg = '乾元—安鑫回报”（按月）开放式净值型人民币理财产品净值公告'
            inner_html = re.search(reg, item)
            if inner_html and flag:
                inner_url = re.search('href="([^"]*)"', item).group(1)
                inner_url = self.start_urls[0] + inner_url[2:]
                # inner_title = re.search('title="([^"]*)"', item).group(1)
                req = urllib.request.urlopen(inner_url)
                res = req.read()
                reg_2 = '(年.*日)年化收益率为([^%^。]*%)'
                latest_rate = re.search(reg_2, res.decode('utf-8'))
                if latest_rate:
                    latest_rate = latest_rate.group(2) + '(2018' + latest_rate.group(1) + ')'
                    rates_line.append(latest_rate)
                    csv_to_change = pd.read_csv('./result/ccb_funds.csv')
                    csv_to_change.prate[csv_to_change.pid == 'GD072016001000Y01'] = rates_line[0]
                    csv_to_change.to_csv('./result/ccb_funds.csv', encoding='utf_8_sig', index=False)
                    self.crawler.engine.close_spider(self, '数据修改完毕，收工！')

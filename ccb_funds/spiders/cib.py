# -*- coding: utf-8 -*-
# 兴业银行
import scrapy
import re
import urllib
from urllib import request
from ccb_funds.items import FundsInfoItem


class Cibbank(scrapy.Spider):
    name = "cib"
    allowed_domains = ["cib.com"]
    start_urls = ['http://wealth.cib.com.cn/retail/onsale/index.html',
                  'http://wealth.cib.com.cn/retail/onsale/open.html',
                  'http://wealth.cib.com.cn/retail/onsale/cash.html',
                  'http://wealth.cib.com.cn/retail/onsale/zyb.html']

    def start_requests(self):
        for i in range(len(self.start_urls)):
            yield scrapy.FormRequest(
                url=self.start_urls[i],
                method = 'GET',
                callback=self.parse)

    def parse(self, response):
        # print "内部网页"
        # print response.body
        tables = response.xpath('//table')
        # print len(indatas)
        for table in tables:
            floor = 5
            rate = 6
            period = 4
            table_head = table.xpath('./thead')
            if len(table_head)>0:
                for data in table.xpath('./tbody/tr'):
                    item = FundsInfoItem()

                    item["pname"] = data.xpath('./td')[0].xpath('string(.)').extract()[0]

                    item["pid"] = data.xpath('./td')[-1].xpath('./img/@src').extract()[0].split('lccp')[-1].split('.')[0]

                    item["prate"] = data.xpath('./td')[rate].xpath('./text()').extract()[0]
                
                    item["pfloor"] = data.xpath('./td')[floor].xpath('./text()').extract()[0]
                
                    item["pperiod"] = data.xpath('./td')[period].xpath('./text()').extract()[0]

                    yield item
            else:
                table_title = table.xpath('./tbody/tr')[0].xpath('./td')
                for i in range(len(table_title)):
                    title = table_title[i].xpath('string(.)').extract()[0]
                    # print title
                    if u'起购' in title:
                        floor = i
                    elif u'客户年化' in title or u'比较基准' in title or u'客户参考浮动年化净收益率' in title:
                        rate = i
                    elif u'天' in title:
                        period = i
                for data in table.xpath('./tbody/tr')[1:]:
                    item = FundsInfoItem()

                    item["pname"] = data.xpath('./td')[0].xpath('string(.)').extract()[0]

                    item["pid"] = data.xpath('./td')[-1].xpath('./img/@src').extract()[0].split('lccp')[-1].split('.')[0]

                    item["prate"] = data.xpath('./td')[rate].xpath('./text()').extract()[0]
                    if item['prate'] == '以我行网站刊登的参考收益率公告为准':
                        try:
                            html_id = '201' + str(item["pid"][-4:-1])
                            if html_id == '201201':
                                html_id = '201203'
                            inner_url_1 = 'http://wealth.cib.com.cn/retail/duration/cash/referNetValue/' + html_id + '/' + \
                                          html_id + '.html'
                            res = urllib.request.urlopen(inner_url_1)
                            inner_html_1 = res.read().decode('utf-8')
                            re_1 = '(/retail/duration/cash/referNetValue/' + html_id + '/'\
                                   + html_id + '_[\d]*.html)'
                            inner_url_2 = re.search(re_1, inner_html_1).group()
                            inner_url_2 = 'http://wealth.cib.com.cn' + inner_url_2
                            res_2 = urllib.request.urlopen(inner_url_2)
                            inner_html_2 = res_2.read().decode('utf-8')
                            re_2 = '<td>([\d\.]*%)</td>'
                            final = re.search(re_2, inner_html_2).group(1)
                            item['prate'] = final
                        except Exception as e:
                            print('errorinfo:{}'.format(e))
                            item['prate'] = '未能在子页面获取到收益'
                    item["pfloor"] = data.xpath('./td')[floor].xpath('./text()').extract()[0]
                    item["pperiod"] = data.xpath('./td')[period].xpath('./text()').extract()[0]
                    for sub_item_key in item.keys():
                        item[sub_item_key] = str(item[sub_item_key]).replace('\r', '').replace('\n', '')\
                            .replace('\t', '').strip()
                        print(item[sub_item_key])
                    yield item
        

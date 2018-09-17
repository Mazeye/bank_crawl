# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import pandas as pd


class CcbFundsPipeline(object):

    def open_spider(self, spider):
        if spider.name[-9:] == '_appendix':
            spider_name = spider.name[:-9]
        else:
            spider_name = spider.name
        self.filename = "result/{}_funds.csv".format(spider_name)
        self.spider_name = spider_name
        # self.file_name = open("{}_funds.txt".format(spider.name), "a")

    def process_item(self, item, spider):
        # 这里是将item先转换成字典，在又字典转换成字符串
        temp = []
        temp.append(dict(item))
        text = json.dumps(temp, ensure_ascii=False)
        dft = pd.read_json(text, orient='records')
        try:
            dfin = pd.read_csv(self.filename, encoding='utf_8_sig')
            self.dfout = dft.append(dfin)
        except IOError:
            self.dfout = dft
        self.dfout = self.dfout.drop_duplicates().sort_values('pname')
        if self.spider_name == 'czb':
            self.dfout = self.dfout[['pname', 'pid', 'prate', 'pfloor', 'pperiod', 'pscale']]
        elif self.spider_name == 'hxb':
            self.dfout = self.dfout[['pname', 'prate', 'pfloor', 'pperiod']]
        else:
            self.dfout = self.dfout[['pname', 'pid', 'prate', 'pfloor', 'pperiod']]
        self.dfout.to_csv(self.filename, encoding='utf_8_sig', index=False)
        return item

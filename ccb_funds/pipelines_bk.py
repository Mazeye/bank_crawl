# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import pandas as pd

class CcbFundsPipeline(object):

    def open_spider(self, spider):
        self.filename = "{}_funds.csv".format(spider.name)

    	# self.file_name = open("{}_funds.txt".format(spider.name), "a")


    def process_item(self, item, spider):
        # 这里是将item先转换成字典，在又字典转换成字符串
        # json.dumps转换时对中文默认使用的ascii编码.想输出真正的中文需要指定 ensure_ascii=False
        # 将最后的item 写入到文件中
        temp = []
        temp.append(dict(item))
        text = json.dumps(temp, ensure_ascii=False)
        dft=pd.read_json(text,orient='records',encoding='utf_8_sig')
        try:
            dfin = pd.read_csv("{}_funds.csv".format(spider.name)) 
            self.dfout = dfin.append(dft)
        except IOError:
            self.dfout = dft
        self.dfout.to_csv(self.filename,encoding='utf_8_sig',index=False)
        return item

    # def close_spider(self):
    #     self.dfout.to_csv('test1.csv',encoding='UTF-8',index=False)
        # self.file_name.close()

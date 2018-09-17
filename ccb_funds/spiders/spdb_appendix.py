# -*- coding: utf-8 -*-
import scrapy
import json
from ccb_funds.items import FundsInfoItem


class SpdbSpiderAppendix(scrapy.Spider):
    name = 'spdb_appendix'
    allowed_domains = ['spdb.com.cn']
    start_urls = ['https://ebank.spdb.com.cn/nbper/FinanceFixListQuery.do',
                  'http://per.spdb.com.cn/was5/web/search']

    def start_requests(self):
        for i in range(1, 10):
            # 查找类别3（固定期限）与4（现金管理）
            for type in [3, 4]:
                curpage = i
                yield scrapy.FormRequest(
                    url=self.start_urls[1],
                    formdata={'channelid': '266906',
                              'metadata': 'finance_state|finance_no|finance_allname|finance_anticipate_rate|'
                                          'finance_limittime|finance_lmttime_info|finance_type|docpuburl|'
                                          'finance_ipo_enddate|finance_indi_ipominamnt|finance_indi_applminamnt|'
                                          'finance_risklevel|product_attr|finance_ipoapp_flag|finance_next_openday',
                              'searchword': '(product_type={})*finance_limittime = %*(finance_currency = 01)'
                                            '*(finance_state=\'可购买\')'.format(str(type)),
                              'page': str(curpage)},
                    method='POST',
                    callback=self.parse)

    def parse(self, response):
        datas = json.loads(response.text)['rows']
        # print(datas[1])
        for data in datas:
            item = FundsInfoItem()
            item["pid"] = data['finance_no']
            item["pname"] = data['finance_allname']
            item["prate"] = data['finance_anticipate_rate']
            # 利率格式归一化
            item["prate"] = item["prate"].replace('％', '').replace('\r', '').replace('\n', '').replace('\t', '')
            if item["prate"][-1] != '%':
                item["prate"] = item["prate"] + '%'
            item["pperiod"] = data['finance_lmttime_info']
            item["pfloor"] = data['finance_indi_ipominamnt']
            yield item

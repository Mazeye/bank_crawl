# -*- coding: utf-8 -*-
import scrapy
import re
from ccb_funds.items import FundsInfoItem


class SpdbSpider(scrapy.Spider):
    name = 'spdb'
    allowed_domains = ['spdb.com.cn']
    start_urls = ['https://ebank.spdb.com.cn/nbper/FinanceFixListQuery.do',
                  'http://per.spdb.com.cn/was5/web/search']

    def start_requests(self):
        for search_type in [1, 2, 4, 5]:
            for begin_n in range(0, 100, 10):
                if begin_n == 0:
                    begin_n = 1
                yield scrapy.FormRequest(
                    url=self.start_urls[0],
                    formdata={
                        '_viewReferer':	'default,finance/bankfinance/FinanceQueryList',
                        # Abstract
                        'BeginNumber': str(begin_n),
                        'BeginNumberFlag':'1',
                        # CurrencyNo
                        'CurrencyNoMoreFlag':'0',
                        # EVoucherAmount
                        # EVoucherNo
                        # Finance
                        'FinanceAnticipateor':'3',
                        'FinanceBuyLimitMoneyor':'3',
                        'financeChangeFlag':'financeChangeFlag2',
                        # FinanceClientType
                        'FinanceFlag':'0',
                        'FinanceHotsellFlag':'1',
                        # FinanceIsTrans
                        'FinanceLimitMoreFlag':	'0',
                        'Financelimittimetypeor':	'3',
                        # FinanceNo
                        # FinanceProductNavType
                        # FinanceQueryTerm
                        # FinanceQueryType
                        # FinanceSearchLimitTime
                        # FinanceSearchStatus
                        'FinanceSearchType': '0'+str(search_type),
                        'FinanceSellOrderFlag':	'1',
                        'FinanceShowRateOrder':	'3',
                        # FinanceStartAmount
                        'FinanMoveFlag':'1',
                        # fourMenuId
                        'FromMemu':	'1',
                        'islogined': '0',
                        # isNewFinancial
                        # MenuID
                        # OptionFinanceNo
                        # OptionFinancePrdIncomeInfoLevel
                        'PersonBankFlag':	'01',
                        'QueryNumber':	'10',
                        'searchFlag':	'0',
                        'selectedMenu':	'menu3_1_1',
                        # selectedSubMenu
                        'SkipPageTage':	'loadSkipPage',
                        # toPageNo
                        # UseEVoucher
                        },
                    method='POST',
                    callback=self.parse)

    def parse(self, response):
        re_pid = re.compile(r'(2301\d*)</font>')
        re_pname = re.compile(r'<fontclass="autosho[^>]*>([^<]*)|<fontclass="xianjin[^>]*>([^<]*)')
        re_prate = re.compile(r'1-2">([^<]*)<|准-->([^<]*)<')
        re_pperiod = re.compile(r'日-->([^<]*)<|td>([0123456789天月年\-]+)<')
        re_pfloor = re.compile(r'aid[^>]*>([^<]*)|位-->([^<]*)|td>([^<]*万元)')
        res_clean = response.text.replace(' ', '').replace('\r', '').replace('\n', '').replace('\t', '')
        pids = re_pid.findall(res_clean)
        pnames = re_pname.findall(res_clean)
        prates = re_prate.findall(res_clean)
        pperiods = re_pperiod.findall(res_clean)
        pfloors = re_pfloor.findall(res_clean)
        datas = []
        for i in range(len(pids)):
            data = [pids[i], pnames[i][0], prates[i][0], pperiods[i][0], pfloors[i][0]]
            if data[1] == '':
                data[1] = pnames[i][1]
            if data[2] == '':
                data[2] = prates[i][1]
            if data[3] == '':
                data[3] = pperiods[i][1]
            if data[3] == '':
                data[3] = '无'
            if data[4] == '':
                data[4] = pfloors[i][1]
            if data[4] == '':
                data[4] = pfloors[i][2]
            datas.append(data)

        for data in datas:
            item = FundsInfoItem()
            item["pid"] = data[0]
            item["pname"] = data[1]
            item["prate"] = data[2]
            # 利率格式归一化
            item["prate"] = item["prate"].replace('％', '').replace('\r', '').replace('\n', '').replace('\t', '')
            try:
                if item["prate"][-1] != '%':
                    item["prate"] = item["prate"] + '%'
            except Exception as e:
                print('Error:{}'.format(e))
                print(item["prate"])
            item["pperiod"] = data[3]
            item["pfloor"] = data[4]
            yield item
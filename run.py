import subprocess
import json
import time
import pandas as pd
subprocess.call('scrapy crawl spdb')
subprocess.call('scrapy crawl spdb_appendix')
subprocess.call('scrapy crawl cmbc')
subprocess.call('scrapy crawl cmbc_appendix')
subprocess.call('scrapy crawl citicbank')
subprocess.call('scrapy crawl cib')
subprocess.call('scrapy crawl cgb')
subprocess.call('scrapy crawl ccb')
subprocess.call('scrapy crawl ccb_appendix')
subprocess.call('scrapy crawl icbc')
subprocess.call('scrapy crawl abc')
subprocess.call('scrapy crawl boc')
subprocess.call('scrapy crawl bcm')
subprocess.call('scrapy crawl ceb')
subprocess.call('scrapy crawl hxb')
subprocess.call('scrapy crawl pingan')
subprocess.call('scrapy crawl czb')
subprocess.call('scrapy crawl hfbank')

# 合并最终结果数据表
bank_dict_file = open('./config/bank_dict.json', 'rb')
bank_dict_raw = bank_dict_file.read().decode('utf-8')
bank_dict = json.loads(bank_dict_raw)
bank_dict_file.close()
cur_time = time.strftime('%Y%m%d',time.localtime(time.time()))
writer = pd.ExcelWriter('./output/output_{}.xlsx'.format(cur_time))
for key in bank_dict.keys():
    try:
        data1 = pd.read_csv('./result/{}_funds.csv'.format(bank_dict[key]))
        data1.rename(columns={'pname': '产品名称', 'pid': '产品代码',
                         'prate': '预期年化收益率/业绩基准', 'pfloor': '起购金额',
                         'pperiod': '期限', 'pscale': '发行规模'}, inplace=True)
        data1.to_excel(writer, sheet_name=key.replace('银行', ''), index=False)
    except Exception as e:
        print('读取"{}"爬取结果文件{}失败'.format(key, bank_dict[key]))
        print('errMsg:{}'.format(e))
writer.close()

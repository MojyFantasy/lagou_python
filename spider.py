# coding: utf-8
import traceback
from multiprocessing.pool import Pool

import pymongo
import requests
import time
from bs4 import BeautifulSoup as bs

from config import MONGO_URL, MONGO_DB, MONGO_TABLE

URL = "https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false&isSchoolJob=0"
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
total_count = 1462

def get_page_content(url, page, keyword):
    headers = {
        'User-Agent':
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36",
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.6,ja;q=0.4,en;q=0.2',
        'Host': 'www.lagou.com',
        'Origin': 'https://www.lagou.com',
        'Referer': 'https://www.lagou.com/jobs/list_python?labelWords=&fromSearch=true&suginput=',
    }
    data = {
        'first': 'true',
        'pn': page,
        'kd': keyword
    }
    try:
        print('start to request page ', page)
        response = requests.post(url, data=data, headers=headers)
        if response.status_code == 200:
            print('succeed to request page ', page)
            return response.json()
        return None
    except:
        print(traceback.format_exc())
        return None


def parse_page_content(content):
    print(content)
    if content.get('success') is not True:
        return None
    data = content.get('content', {})
    position_info = data.get('positionResult', {})
    position_res = position_info.get('result', {})
    for position in position_res:
        company_name = position.get('companyShortName', '')
        create_time = position.get('createTime')
        salary = position.get('salary')
        work_year = position.get('workYear')
        education = position.get('education')
        city = position.get('city')
        position_name = position.get('positionName')
        yield {
            'company_name': company_name,
            'create_time': create_time,
            'salary': salary,
            'work_year': work_year,
            'education': education,
            'city': city,
            'position_name': position_name
        }


def save_to_db(result):
    if db[MONGO_TABLE].insert(result):
        print("存储数据到MONGODB成功！", result)
        return True
    return False


def main(page_num, keyword="python"):
    content = get_page_content(URL, page_num, keyword)
    for position in parse_page_content(content):
        print(position)
        save_to_db(position)


if __name__ == '__main__':
    # pool = Pool()
    # pool.map(main, [i for i in range(2, int(total_count/15)+1)])
    for i in range(4, int(total_count/15)+1):
        main(i)
        time.sleep(3)

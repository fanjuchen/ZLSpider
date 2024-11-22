import time

import requests
import tqdm
from bs4 import BeautifulSoup
import pandas as pd
# 导入
import time
from DrissionPage import Chromium
import re

def get_job_dict():
    tab = browser.latest_tab
    dic = {}
    for job in job_list:
        tab.get('https://www.zhaopin.com/sou/jl%E7%A6%8F%E5%B7%9E/kw/p1?kt=3')
        inp = tab.ele('xpath://*[@id="filter-hook"]/div/div[1]/div/div[1]/input')
        time.sleep(1)
        inp.clear(by_js=True)
        inp.input(job)
        time.sleep(1)
        tab.ele('xpath://*[@id="filter-hook"]/div/div[1]/div/button').click()
        tab.wait.load_start()  # 等待页面进入加载状态
        print(tab.url)

        kwd = re.findall('kw(.*?)/p1\?', str(tab.url))
        print(kwd)
        # time.sleep(1)
        dic[job] = kwd
    print(dic)
    return dic







if __name__ == '__main__':
    # 连接浏览器
    browser = Chromium()
    # 获取标签页对象

    job_list = [
        "Java开发", "UI设计师", "Web前端", "PHP", "Python", "Android", "美工",
        "深度学习", "算法工程师", "Hadoop", "Node.js", "数据开发",
        "数据分析师", "数据架构", "人工智能", "区块链", "电气工程师",
        "电子工程师", "PLC", "测试工程师", "设备工程师", "硬件工程师",
        "结构工程师", "工艺工程师", "产品经理", "新媒体运营", "运营专员",
        "淘宝运营", "天猫运营", "产品助理", "产品运营", "淘宝客服",
        "游戏运营", "编辑"
    ]
    jobs = get_job_dict()
    # jobs = {'Java开发': ['01500O80EO062NO0AF8G'], 'UI设计师': ['01AG0ICBNQ5Q2NG8'], 'Web前端': ['01BG0P80C994QUNF'],
    #         'PHP': ['01800I00A0'], 'Python': ['01800U80EG06G03F01N0'], 'Android': ['010G0RG0CG07403F01KG0P0'],
    #         '美工': [], '深度学习': ['DNOLT9IRCP760'], '算法工程师': ['FEBMPLATSLT0MNG8'],
    #         'Hadoop': ['01400O80CG06U03F01O0'], 'Node.js': ['01700RO0CG06A01E01L00SO'], '数据开发': ['CLO66RIV019T2'],
    #         '数据分析师': ['CLO66RII0PJP0NG8'], '数据架构': ['CLO66RJ7MPJO8'], '人工智能': ['9QT5RPB6FA0FQ'],
    #         '区块链': ['ACT5ELSKVO'], '电气工程师': ['EKQMO52TSLT0MNG8'], '电子工程师': ['EKQLMK2TSLT0MNG8'], 'PLC': [],
    #         '测试工程师': ['DL5ONLATSLT0MNG8'], '设备工程师': ['HEV5I1QTSLT0MNG8'], '硬件工程师': [],
    #         '结构工程师': ['FR9MF12TSLT0MNG8'], '工艺工程师': ['BNIO4UITSLT0MNG8'], '产品经理': ['9QJL9GBUPTQ0C'],
    #         '新媒体运营': ['CMO5L4IFAE7T1115'], '运营专员': ['HV8889AE2DA5G'], '淘宝运营': ['DNC5N7CFQ222A'],
    #         '天猫运营': ['B4KN6ASFQ222A'], '产品助理': ['9QJL9GAIL5Q0C'], '产品运营': [], '淘宝客服': ['DNC5N7ARK9JGQ'],
    #         '游戏运营': [], '编辑': ['FSB8V48']}

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0",
        # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        # "Accept-Language": "en-US,en;q=0.5",
        # "Connection": "keep-alive",
    }
    pages = 50
    urls = [['https://www.zhaopin.com/sou/jl%E7%A6%8F%E5%B7%9E/kw{}/p{}?kt=3'.format(item[0], page) for page in range(1, pages + 1)] for item in list(jobs.values()) if len(item)]
    urls = sum(urls, [])
    results = []
    for url in tqdm.tqdm(urls):
        try:
            res = requests.get(url, headers=headers)

            soup = BeautifulSoup(res.text, 'lxml')
            job_list = soup.find_all('div', class_='joblist-box__item clearfix')

            for job in job_list:
                try:
                    jobinfo_name = job.find('a', class_='jobinfo__name').text.replace('\n', '').strip()
                    link = job.find('a', class_='jobinfo__name')['href']

                    salary = job.find('p', class_='jobinfo__salary').text.replace('\n', '').strip()
                    tag = job.find_all('div', class_='joblist-box__item-tag')
                    tag = [item.text.replace('\n', '').strip() for item in tag]
                    tag = "|".join(tag)
                    other_info = job.find_all('div', class_='jobinfo__other-info-item')
                    location = other_info[0].text.replace('\n', '').strip()
                    exp = other_info[1].text.replace('\n', '').strip()
                    edu = other_info[2].text.replace('\n', '').strip()
                    company_name = job.find('a', class_='companyinfo__name').text.replace('\n', '')
                    print(
                        jobinfo_name, company_name, salary, tag, location, exp, edu, link
                    )
                    results.append([
                        jobinfo_name, company_name, salary, tag, location, exp, edu, link
                    ])
                except Exception as e:
                    print(e)
        except Exception as page_err:
            print('page err', page_err)

        time.sleep(1)

    df = pd.DataFrame(results)
    df.to_csv('zhilian.csv', encoding='utf_8_sig', index=False)
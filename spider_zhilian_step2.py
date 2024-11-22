import pandas as pd
import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup
import nest_asyncio

# 应用 nest_asyncio，解决事件循环冲突问题
nest_asyncio.apply()

CONCURRENT_TASKS = 5  # 控制每个浏览器的并发任务数量


async def fetch_data(row, browser, semaphore):
    """单个任务的爬取逻辑"""
    try:
        async with semaphore:  # 限制并发
            url = row[-1]
            print(f"Fetching URL: {url}")
            page = await browser.newPage()
            await page.goto(url, timeout=30000)  # 设置超时时间
            await asyncio.sleep(2)  # 等待页面加载

            content = await page.content()
            soup = BeautifulSoup(content, 'lxml')

            # 提取数据
            update_time = soup.find('span', class_='summary-plane__time')
            update_time = update_time.text.replace('\n', '').strip() if update_time else '未知'

            duty = soup.find('div', class_='describtion')
            duty = duty.text.replace('\n', '').strip() if duty else '未知'

            info = soup.find('ul', class_='summary-plane__info')
            if info:
                sums = info.find_all('li')[-1].text.replace('\n', '').strip()
                if '人' not in sums:
                    sums = '未知'
            else:
                sums = '未知'

            # 返回爬取的数据
            row += [update_time, duty, sums]
            print(row)
            await page.close()
            return row
    except Exception as err:
        print(f"Error fetching URL {row[-1]}: {err}")
        return None


async def browser_worker(rows):
    """为每组任务启动一个浏览器实例"""
    semaphore = asyncio.Semaphore(CONCURRENT_TASKS)  # 控制并发任务数量
    browser = await launch(headless=True, args=['--no-sandbox'], executablePath='C:\Program Files\Google\Chrome\Application\chrome.exe')  # 启动浏览器
    tasks = [fetch_data(row, browser, semaphore) for row in rows]
    results = await asyncio.gather(*tasks)
    await browser.close()
    return results


async def main():
    # 读取CSV文件
    df = pd.read_csv('./zhilian.csv')
    rows = [list(row) for _, row in df.iterrows()]

    # 分割任务，每个浏览器实例处理一部分
    num_browsers = 2  # 启动的浏览器实例数量，可根据性能调整
    chunk_size = len(rows) // num_browsers
    chunks = [rows[i:i + chunk_size] for i in range(0, len(rows), chunk_size)]

    # 启动多个浏览器实例并发执行
    results = await asyncio.gather(*[browser_worker(chunk) for chunk in chunks])

    # 合并结果
    final_result = [res for sublist in results for res in sublist if res]

    # 保存结果到CSV
    final_df = pd.DataFrame(final_result)
    final_df.to_csv('./result.csv', index=False, encoding='utf_8_sig')


if __name__ == '__main__':
    asyncio.run(main())

# r'C:\Program Files\Google\Chrome\Application\chrome.exe'
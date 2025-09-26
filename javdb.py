import time
from idlelib import query

import requests
from bs4 import BeautifulSoup

javlibrary_search_url = "https://javdb.com/search"

javlibrary_cookie = "list_mode=h; theme=auto; locale=zh; _ym_uid=1743432317221724263; _ym_d=1743432317; over18=1; notification_hide=1; _rucaptcha_session_id=aeb8e1e16070023e99b6ea06ff0405f3; remember_me_token=eyJfcmFpbHMiOnsibWVzc2FnZSI6IklrRjZhMXBmZUhWaU5tOXBRMjk1YTFkaVdVSk9JZz09IiwiZXhwIjoiMjAyNS0wOS0xNFQwODozMDoxOC4wMDBaIiwicHVyIjoiY29va2llLnJlbWVtYmVyX21lX3Rva2VuIn19--1853b4fea96fd1de23a2fa9c295f05cddee7ac25; cf_clearance=ZwIYtxKn5VAnCGmYcrPskmAhJpkqnpCQwkFgBWA4AKg-1757261920-1.2.1.1-k5CnnM7IXyEmjo.ARDFHB4hPr5lTVvrnmnu8oymCABAbjbAMfyg4rb0cnFQ60ZK_RrNC5dOYOt3x64zr08hBiCrQumztTlgeuvtlQQBfhMzuKemeigpxXo4xxN7Uj11K8SRvLKF8iL__fQHvtKav5krUGhImdA9cUKLN9UbFGvluLNZxJsjTZcW8QIM08IkauqtzfMRgJSuHNVsjor7uhncNqs_wS0VcD0LZvTAS1Xw; _jdb_session=AQ2A4ZldNfmzAx9ssCCoqjcYM7Cl8NocTq%2BtbkBZ6pXKVuEYFNs1RUpgcOT9JDABFYFk19ALsPWUpveOhpsQinNWiZXy%2BaFDZh2OApBQjRPF6qAFA8h1PCpING3ajCBaoH%2FO8B1kyPkNcnIjRNNyUU0674RRBjU7pOpviXoTMhqC7yJ3B0kfiTeDQ9w1dxy2%2BzVPGq99AEHbeObjOB%2BUW8wve%2FKjmIWGDz2m6HNBFt79uTRlfwXES0jHr8Ui%2FYQ7tDy0yQcX%2FjwpBTJHAQUALaORtKHhTCHCzKcLE29dWN%2FhjFAr9DIxPMut5vrgUKpy5qE46xzgCuHA%2Bnhx%2BIx7voZdcUkom2ymwwaXoZRnPov4oDOVJx24JEMI3MVWw%2Bl8SNc%3D--rOQzGWnXB8hFQFX0--OrDD%2FAbSalRZ%2BtP66jLdeg%3D%3D"
proxies = {
    "https": "http://127.0.0.1:10809"
}

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    "cookie": javlibrary_cookie
}
import re
def normalize_code(code):
    # Use regular expression to remove leading zeros from the numeric part
    return re.sub(r'(\D+)-?0*(\d+)', r'\1-\2', code)

def getletterinfo(query):
    url = f"{javlibrary_search_url}?q={query}&f=all"
    print(url)
    r = requests.get(url, headers=headers, proxies=proxies)

    soup = BeautifulSoup(r.text, 'html.parser')

    items = soup.select('.movie-list .item')

    serachlist = []

    for item in items:
        a_tag = item.find('a', class_='box')
        href_value = a_tag.get('href') if a_tag else None
        strong_text = item.find('strong').text if item.find('strong') else None
        video_title = item.find('div', class_='video-title').text.strip() if item.find('div',
                                                                                       class_='video-title') else None
        info = {}
        info["href_value"] = f"https://javdb.com{href_value}"
        info["strong_text"] = strong_text
        info["video_title"] = video_title
        serachlist.append(info)
        print(f"链接: {href_value}, 标签: {strong_text}, 内容: {video_title}")

    for info in serachlist:

        if (normalize_code(query).lower() in normalize_code(info.get("strong_text")).lower()) or  (normalize_code(info.get("strong_text")).lower() in normalize_code(query).lower() ) :
            print(info["href_value"])
            r1 = requests.get(info["href_value"], headers=headers, proxies=proxies)

            soup1 = BeautifulSoup(r1.text, 'html.parser')
            # 提取信息并存储到 videoinfo 字典中
            videoinfo = {}
            # 定位到h2元素
            h2_tag = soup1.find('h2', class_='title is-4')
            # 从h2元素获取所有下一级的strong元素
            strong_tags = h2_tag.find_all('strong')

            # 提取信息并存储到 videoinfo 字典中
            videoinfo = {}

            # 获取番号
            videoinfo['video_id'] = strong_tags[0].get_text(strip=True) if strong_tags else None

            # 获取标题
            videoinfo['video_title'] = videoinfo['video_id'] + " " + strong_tags[1].get_text(strip=True) if len(
                strong_tags) > 1 else None

            # 检查是否存在 origin-title，并替换 video_title
            origin_title_span = h2_tag.find('span', class_='origin-title')
            if origin_title_span:
                origin_title = origin_title_span.get_text(strip=True)
                videoinfo['video_title'] = videoinfo['video_id'] + " " + origin_title

            # 获取演员
            # 提取演员信息
            actor_tag = soup1.find('strong', text='演員:').find_next_sibling('span')
            actor_names = []

            if actor_tag:
                # 查找所有的演员链接和对应的性别符号
                actors = actor_tag.find_all('a')
                symbols = actor_tag.find_all('strong', class_='symbol')

                for actor, symbol in zip(actors, symbols):
                    actor_name = actor.get_text(strip=True)
                    gender = 'female' if 'female' in symbol.get('class', []) else 'male'
                    actor_names.append((actor_name, gender))

                # 按照性别排序，女性优先
                actor_names.sort(key=lambda x: x[1])
            # 只保留名字
            videoinfo['actor_names'] = [name for name, gender in actor_names]

            # 获取日期
            actor_tag = soup1.find('strong', text='日期:').find_next_sibling('span')
            video_date = actor_tag.text.strip() if actor_tag else None
            videoinfo['发行日期'] = video_date

            # 获取時長
            actor_tag = soup1.find('strong', text='時長:').find_next_sibling('span')
            video_long = actor_tag.text.strip() if actor_tag else None
            videoinfo['长度'] = video_long

            try:
                # 获取评分
                rating_tag = soup1.find('strong', text='評分:').find_next_sibling('span')
                rating = rating_tag.text.strip() if rating_tag else None
                videoinfo['rating'] = rating
            except:
                print("找不到评分")


            # 获取图片URL
            image_url = soup1.find('img', class_='video-cover')['src']
            videoinfo['image_url'] = image_url if image_url.startswith(
                'http') else f"https://c0.jdbstatic.com{image_url}"
            return videoinfo

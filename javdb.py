import time
from idlelib import query

import requests
from bs4 import BeautifulSoup

javlibrary_search_url = "https://javdb.com/search"

javlibrary_cookie = "list_mode=h; theme=auto; locale=zh; over18=1; comment_warning=1; _ym_uid=1743432317221724263; _ym_d=1743432317; hide_app_banner=1; cf_clearance=GdJs3UnOyzaEAp9C40Ia7ZhGvpE7R5KJEkvho9F.EA8-1751215328-1.2.1.1-kMZvTGWx0NylMBqYazZK2m1kD.2DJKt9gW0Migkkjdav_ui7O8pyQgrn0xfqkpYy4eifbVLz.drdExFd4Jioon70FZ.trEuw2etnGOD3dPHSgH8_QbI.SOz.2eThBfoK2IUDN1ecgWLcmVVKmgU2ZqakIE6LgH1vw9ddvBgotaJPU3Zl6Rjdq.CFUq6FQo4TyJdQHupwPP7O9cpr_HLjl4wsIbJfWQMqvPIhMfjCOwaCpxEzrtxXe_oqSfz5VaUI83mfOwtsfLWiwr_m3SRTBskfAqmLvN0cP9tFe7Sa3TBYesJy0wyCGu6PDyceND52a0CAIVhh0GmDsghcMeHzgIB1y9mHs4ZriL5lvy_zfEc; _jdb_session=XLWsqlHMifGS5q%2BoNS8IjqEUqKguVLexQCqyylpgAE1hobmQyGgDSi3ZqDMTvcbo%2BOU5JWohryOV2gHFI5LzOHx3dFIwmsE3aMbBiEH6msVRen2G6o%2BYE%2BOF9pCTojS24u3Mc%2FoM8eVrUsr41PFVuao772JKiBKRNHMexJPIG%2BXS%2Fd89OBeorw5yJ%2BZmgfspHkFc17Ney3EkeLOLwoP4oW7%2FLnu3nBNXv5vzr4dsy9eYMj7Zl%2B3kKx056O2XkU42uP7Pxfd65kmJtduvhcqKaXSHgve05AEmg%2F8MuXhsRh8p%2F%2FuOJazypm8ujYEWZqabq%2BiDn8ncXL850x6L5C51FLjga1g30GnXJApTnDQL0ehMg5IMYOlXvIgzNfQx1U5gTok%3D--TTGteI1Q1u1zgl%2FH--IfJ%2Fid791WHvdK5s5itUFg%3D%3D"
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
        if normalize_code(info.get("strong_text")).lower() == normalize_code(query).lower():
            print(info["href_value"])
            r1 = requests.get(info["href_value"])

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

import os
import re
import requests
from bs4 import BeautifulSoup


def find_alpha_num_combinations(s):
    # 正则表达式匹配字母后紧跟数字的组合
    matches = re.findall(r'([A-Za-z]+)[^\w]*(\d+)', s)

    # 为每个匹配的组合插入连字符
    separated = ['{}-{}'.format(match[0], match[1]) for match in matches]

    return separated


def download_picture(image_url, actor_folder):
    response = requests.get(image_url)
    # 确保请求成功
    if response.status_code == 200:
        # 分割URL以获取文件名
        filename = image_url.split('/')[-1]

        if (os.path.exists(actor_folder)):
            filename = os.path.join(actor_folder, filename)
        # 打开文件以写入二进制内容
        with open(filename, 'wb') as file:
            file.write(response.content)

        print(f"{image_url}图片已下载并保存为 {filename}")
    else:
        print(f"{image_url}图片下载失败。")


def parsedownurl(url, old_dir):
    r = requests.get(url, headers=headers, proxies=proxies)
    soup = BeautifulSoup(r.text, 'html.parser')

    try:
        # 查找id为"video_title"的div标签内的a标签
        video_title_a_tag = soup.find('div', id='video_title').find('a')
        # 获取a标签的文本内容
        video_title = video_title_a_tag.get_text(strip=True)
    except:
        print(f"找不到{url}的相关信息")
        return

    actors = soup.find_all('span', class_='cast')

    # 提取并打印所有演员的名字
    actor_names = []
    for actor in actors:
        # 找到<a>标签并获取其文本内容
        name_tag = actor.find('a')
        if name_tag:
            actor_names.append(name_tag.get_text())

    if len(actor_names) == 1:
        actor_name = actor_names[0];
        actor_folder = os.path.join(dir_path, actor_name)
        print(actor_folder)
        if not os.path.exists(actor_folder):
            os.makedirs(actor_folder)
        actor_folder = actor_folder
    elif len(actor_names) == 0:
        print("没有演员")
    else:
        actor_name = actor_names[0];
        actor_folder = os.path.join(dir_path, actor_name)
        print(actor_folder)
        if not os.path.exists(actor_folder):
            os.makedirs(actor_folder)
        actor_folder = actor_folder

    video_folder = os.path.join(actor_folder, video_title)
    if not os.path.exists(video_folder):
        os.rename(old_dir, video_folder)
    else:
        os.remove(video_folder)
        os.rename(old_dir, video_folder)

    img_tag = soup.find('img', id='video_jacket_img')

    # 提取src属性
    image_url = img_tag['src'] if img_tag else None

    # 如果找到了图片URL，则下载图片
    if image_url:
        print(f"图片地址：{image_url}")
        try:
            download_picture(image_url, video_folder)
        except:
            print(f"图片地址：{image_url}下载失败")

    video_info = {}
    video_info['video_title'] = video_title
    video_info['image_url'] = image_url

    # 提取信息
    video_info['识别码'] = soup.find('td', text='识别码:').find_next_sibling('td').text
    video_info['发行日期'] = soup.find('td', text='发行日期:').find_next_sibling('td').text
    video_info['长度'] = soup.find('td', text='长度:').find_next_sibling('td').text.strip() + '分钟'
    video_info['导演'] = soup.find('td', text='导演:').find_next_sibling('td').text.strip()
    video_info['制作商'] = soup.find('td', text='制作商:').find_next_sibling('td').text.strip()
    video_info['发行商'] = soup.find('td', text='发行商:').find_next_sibling('td').text.strip()

    video_info['演员'] = ', '.join(actor_names)

    info_path = "info.txt"
    if (os.path.exists(video_folder)):
        info_path = os.path.join(video_folder, info_path)

    # 将信息写入文件
    with open(info_path, 'w', encoding='utf-8') as file:
        for key, value in video_info.items():
            file.write(f"{key}: {value}\n")

    print("信息已写入info.txt文件。")


javlibrary_search_url = "https://www.javlibrary.com/cn/vl_searchbyid.php?keyword="

javlibrary_cookie = "timezone=-480; dm=javlibrary; cf_clearance=JZQ3WX.lv8WxaFrHQmqtICNh3qh1zcp5Zu3ZWZuImHE-1710561619-1.0.1.1-_RNeskDrpnMp42iAmC.WPZm9sN9xFhKvFwgdoEadqNthrlbK3UFXcAheIMqkXwzPM0cnSBdMKTIS1dQrcqEubA; over18=18"

proxies = {
    "https": "http://127.0.0.1:10809"
}

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    "cookie": javlibrary_cookie
}

dir_path = "D:\\"

entries = os.listdir(dir_path)

for entry in entries:
    mark = find_alpha_num_combinations(entry)
    if (len(mark) != 0):
        print(entry)
        print(mark)
        for letter in mark:
            new_url = javlibrary_search_url + letter
            print(f"entries：{entries}  mark：{mark} \n\r正在解析 {new_url}")
            old_dir = os.path.join(dir_path, entry)
            parsedownurl(new_url, old_dir)

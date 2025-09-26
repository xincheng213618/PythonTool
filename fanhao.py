import re
import shutil
import filecmp
import requests
import javdb
import glob
import time
import os
import stat

def get_non_hidden_non_readonly_items(directory):
    items = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)

        # Check if the item is not hidden
        if not item.startswith('.') and not item.startswith('$')  and not item.startswith('Config') and not item.startswith('System') and not item.startswith('Extera') and not item =='VR' and not item =="noactor":
            # Get the item's mode
            item_mode = os.stat(item_path).st_mode

            # Check if the item is not read-only
            if not (item_mode & stat.S_IWRITE == 0):
                items.append(item)

    return items

def find_alpha_num_combinations(s):
    print (s)
    match = re.match(r'^(\d{6}_\d{2})-[0-9A-Za-z]+$', s)
    if match:
        return [match.group(1)]
    # 数字+英文-数字，直接原样返回
    pattern_num_eng_num_ = r'^\d+[A-Za-z]+-\d+$'
    if re.match(pattern_num_eng_num_, s):
        return [s]

    # 优先处理 FC2 变式
    pattern_fc2 = r'(fc2)[\s\-]*([a-z]*)[\s\-]*(\d+)'
    match = re.search(pattern_fc2, s, re.IGNORECASE)
    if match:
        return [f"FC2-{int(match.group(3)):07d}"]  # FC2-2195395 补7位零，如需3位可改为:03d

    # 标准字母-数字格式，数字补零到三位
    match = re.search(r'([A-Za-z]+)-(\d+)', s)
    if match:
        return [f"{match.group(1).upper()}-{int(match.group(2)):03d}"]



    # Remove everything before and including '@'
    s = re.sub(r'.*@', '', s)

    # 6位数字-3位数字，后半部分补零到三位
    pattern1 = r"(\d{6})-(\d{1,3})"
    match = re.search(pattern1, s)
    if match:
        return [f"{match.group(1)}-{int(match.group(2)):03d}"]

    # 字母+数字组合，数字补零到三位
    pattern3 = r'([A-Za-z]+)[^\w]*(\d+)'
    matches = re.findall(pattern3, s)
    separated = ['{}-{:03d}'.format(m[0].upper(), int(m[1])) for m in matches]

    return separated

def download_picture(image_url, actor_folder):
    response = requests.get(image_url)
    if response.status_code == 200:
        filename = image_url.split('/')[-1]
        if os.path.exists(actor_folder):
            filename = os.path.join(actor_folder, filename)
        print(filename)
        with open(filename, 'wb') as file:
            file.write(response.content)
        print(f"{image_url} 图片已下载并保存为 {filename}")
    else:
        print(f"{image_url} 图片下载失败。")

def sanitize_filename(filename):
    # 特殊字符
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    # 换行符
    filename = filename.replace('\n', '').replace('\r', '')
    # 截断
    max_length = 100
    filename = filename[:max_length]
    # 截断空格
    filename = filename.rstrip()
    return filename

def create_safe_filename(full_path, video_title):
    # 清理文件名
    safe_title = sanitize_filename(video_title)
    # 创建完整路径
    new_name = os.path.join(full_path, safe_title + '.mp4')
    return new_name

def move_and_merge_folders(source_folder, destination_folder):
    if not os.path.exists(destination_folder):
        try:
            os.rename(source_folder, destination_folder)
        except Exception as e:
            print(f"Error renaming {source_folder} to {destination_folder}: {e}")
    else:
        for root, dirs, files in os.walk(source_folder):
            relative_path = os.path.relpath(root, source_folder)
            dest_path = os.path.join(destination_folder, relative_path)

            if not os.path.exists(dest_path):
                try:
                    os.makedirs(dest_path)
                except Exception as e:
                    print(f"Error creating directory {dest_path}: {e}")
                    continue

            for file in files:
                source_file = os.path.join(root, file)
                dest_file = os.path.join(dest_path, file)
                try:
                    if os.path.exists(dest_file):
                        if filecmp.cmp(source_file, dest_file, shallow=False):
                            os.remove(source_file)
                        else:
                            base, ext = os.path.splitext(file)
                            new_file = f"{base}(1){ext}"
                            new_dest_file = os.path.join(dest_path, new_file)
                            counter = 1
                            while os.path.exists(new_dest_file):
                                counter += 1
                                new_file = f"{base}({counter}){ext}"
                                new_dest_file = os.path.join(dest_path, new_file)
                            shutil.move(source_file, new_dest_file)
                    else:
                        shutil.move(source_file, dest_file)
                except Exception as e:
                    print(f"Error moving file {source_file} to {dest_file}: {e}")

            for dir in dirs:
                source_subdir = os.path.join(root, dir)
                dest_subdir = os.path.join(dest_path, dir)
                if not os.path.exists(dest_subdir):
                    try:
                        os.makedirs(dest_subdir)
                    except Exception as e:
                        print(f"Error creating directory {dest_subdir}: {e}")

        try:
            shutil.rmtree(source_folder)
        except Exception as e:
            print(f"Error removing source folder {source_folder}: {e}")




def procese_mp4(dir_path):
    file_paths = get_non_hidden_non_readonly_items(dir_path)
    for item in file_paths:
        basename = os.path.basename(item)
        full_path = os.path.join(dir_path, item)
        if os.path.isfile(full_path):
            if full_path.lower().endswith('.mp4'):
                # 检查是否为8K版本，并处理对应的非8K版本
                if basename.lower().endswith('_8k.mp4'):
                    # 这是8K版本，构建非8K版本的文件名
                    non_8k_basename = re.sub(r'_8k\.mp4$', '.mp4', basename, flags=re.IGNORECASE)
                    non_8k_filepath = os.path.join(dir_path, non_8k_basename)
                    # 如果非8K版本存在，则删除它
                    if os.path.isfile(non_8k_filepath):
                        try:
                            os.remove(non_8k_filepath)
                            print(f"检测到8K版本 '{basename}'，已删除非8K版本 '{non_8k_basename}'")
                        except OSError as e:
                            print(f"删除文件 '{non_8k_filepath}' 时出错: {e}")
                else:
                    # 这是非8K版本，检查是否存在对应的8K版本
                    base, ext = os.path.splitext(basename)
                    eight_k_basename = f"{base}_8K{ext}"
                    eight_k_filepath = os.path.join(dir_path, eight_k_basename)
                    # 如果存在8K版本，则跳过当前文件（后续循环会处理8K版本）
                    if os.path.isfile(eight_k_filepath):
                        print(f"检测到非8K版本 '{basename}' 存在对应的8K版本，将跳过此文件。")
                        continue

                # 从文件名创建文件夹名
                folder_name_base = os.path.splitext(basename)[0]
                # 新增规则：如果文件名包含 .partX，则从文件夹名称中移除
                folder_name = re.sub(r'(\.part\d+|_\d+k|_\d+)', '', folder_name_base, flags=re.IGNORECASE)

                new_folder_path = os.path.join(dir_path, folder_name)
                if not os.path.exists(new_folder_path):
                    os.makedirs(new_folder_path)

                new_file_path = os.path.join(new_folder_path, basename)
                try:
                    shutil.move(full_path, new_file_path)
                    print(f"已将 '{full_path}' 移动到 '{new_file_path}'")
                    full_path = new_folder_path
                    item = folder_name
                except Exception as e:
                    print(f"移动文件时出错: {e}")
                    continue
            else:
                print(f"'{full_path}' 不是一个 .mp4 文件")
                continue



def process_videos():
    dir_path = r"D:\\"
    procese_mp4(dir_path)

    extera_path = os.path.join(dir_path, "Extera")
    if not os.path.exists(extera_path):
        os.makedirs(extera_path)

    vr_path = os.path.join(dir_path, "VR")
    if not os.path.exists(vr_path):
        os.makedirs(vr_path)



    file_paths = get_non_hidden_non_readonly_items(dir_path)
    for item in file_paths:
        basename = os.path.basename(item)
        full_path = os.path.join(dir_path, item)

        prefix = ""
        # 检查是否以 [X]. 开头
        match = re.match(r'(\[[^\[\]]+\]\.)', basename)
        if match:
            prefix = match.group(1)
            print(item, "prefix:", prefix)

        mark = find_alpha_num_combinations(item)
        if mark is None:
            break
        # List of items to filter out
        filter_list = ["kfa-11", "SIS-001", "hhd-800", "com-300", "PrestigePremium"]

        # Filter out unwanted items from mark
        filtered_mark = [letter for letter in mark if letter not in filter_list]
        print(filtered_mark)

        if filtered_mark is None:
            break

        for letter in filtered_mark:
            time.sleep(5)
            try:
                videoinfo = javdb.getletterinfo(letter)
            except:
                print("超时，等待中")
                time.sleep(60)
                try:
                    videoinfo = javdb.getletterinfo(letter)
                except:
                    break
            print(videoinfo)

            if not videoinfo:
                continue

            video_title = videoinfo.get("video_title")
            if not video_title:
                print("找不到title")
                break

            is_vr = "VR" in letter.upper()
            video_title = sanitize_filename(video_title)
            actor_names = videoinfo.get("actor_names", [])
            actor_name = actor_names[0] if actor_names else "noactor"
            if is_vr:
                actor_folder = os.path.join(dir_path, "VR", actor_name)
            else:
                actor_folder = os.path.join(dir_path, actor_name)
            os.makedirs(actor_folder, exist_ok=True)

            video_folder = os.path.join(actor_folder, prefix + video_title)

            mp4_files = glob.glob(os.path.join(full_path, '*.mp4'))
            if len(mp4_files) == 1:
                mp4_file = mp4_files[0]
                new_name = os.path.join(full_path, video_title + '.mp4')
                try:
                    os.rename(mp4_file, new_name)
                    print(f"Renamed '{mp4_file}' to '{new_name}'")
                except Exception as e:
                    print(f"Renamed error: {e}")
            elif len(mp4_files) == 0:
                print(f"No .mp4 files found in {full_path}.")
            else:
                print(f"Error: More than one .mp4 file found in {full_path}.")

            move_and_merge_folders(full_path, video_folder)

            image_url = videoinfo.get("image_url")
            if not image_url:
                print("找不到image_url")
            else:
                try:
                    print(f"图片地址：{image_url}， {video_folder}")
                    download_picture(image_url, video_folder)
                except Exception as e:
                    print(f"图片地址：{image_url} 下载失败: {e}")

            info_path = os.path.join(video_folder, "info.txt")
            with open(info_path, 'w', encoding='utf-8') as file:
                for key, value in videoinfo.items():
                    file.write(f"{key}: {value}\n")
            print("信息已写入info.txt文件。")

            break

        if os.path.exists(full_path):
            print(f"没有成功整理，移动文件夹 {full_path} 到extra {extera_path}")
            shutil.move(full_path, os.path.join(extera_path, item))


if __name__ == "__main__":
    import clean
    directory_to_search = "D:\\"
    keywords_to_match = ["美女荷官","杏吧","社区最新情报","妹妹在精彩表演","manko.fun","sex8.cc","u u r","UUE","offkab@sukebei","tuu32.com","新片首发 每天更新 同步日韩","[资源推荐]！下载地址","#第一会所sis001.com最新地址",".gif","最 新 位 址 獲 取 ","1024草榴社區","2048",".apk","18+游戏大全","x u u ","uur9 3.com","新 片 首 發","有趣的台湾妹妹直播",".chm",".html",".mht",".url","有 趣 的 臺 灣 妹 妹 直 播","1063715@18p2p.com.txt","三 上 悠 亚 想 要 跟 你 决 胜 负","电 竞 直 播 平台"," 福 利 机 置","安卓二维码","最新地址.png","最新地址获取.txt","苍 老 师 强 力 推 荐.mp4","女神在线视频","最新网址","更多高清影片访问","18+游戏大全", "聚 合 全 網 H 直 播", "社 區 最 新 情 報","最 新 位 址 獲 取.txt","台 妹 子 線 上 現 場 直 播 各 式 花 式 表 演.mp4"]  # 修改为你的目标关键字

    clean.delete_matching_files_and_empty_dirs(directory_to_search, keywords_to_match)

    process_videos()
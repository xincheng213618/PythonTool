import re
import shutil
import filecmp
import requests
import javdb
import glob
import time
import os
import stat

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

def get_non_hidden_non_readonly_items(directory):
    items = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)

        # Check if the item is not hidden
        if not item.startswith('.') and not item.startswith('$') and not item.startswith('VR') and not item.startswith('Config') and not item.startswith('System') and not item.startswith('Extera'):
            # Get the item's mode
            item_mode = os.stat(item_path).st_mode

            # Check if the item is not read-only
            if not (item_mode & stat.S_IWRITE == 0):
                items.append(item)

    return items

dir_path = r"D:\\"
file_paths = get_non_hidden_non_readonly_items(dir_path)

extera_path = os.path.join(dir_path, "Extera")
if not os.path.exists(extera_path):
    os.makedirs(extera_path)

for item in file_paths:
    full_path = os.path.join(dir_path, item)
    if os.path.isfile(full_path):
        if full_path.lower().endswith('.mp4'):
            folder_name = os.path.splitext(item)[0]
            new_folder_path = os.path.join(dir_path, folder_name)
            if not os.path.exists(new_folder_path):
                os.makedirs(new_folder_path)
            new_file_path = os.path.join(new_folder_path, item)
            shutil.move(full_path, new_file_path)
            full_path = new_folder_path
        else:
            print(f"{full_path} 不是一个 .mp4 文件，跳过文件夹处理逻辑")
            continue

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

        video_title = sanitize_filename(video_title)

        actor_names = videoinfo.get("actor_names", [])
        if not actor_names:
            print("没有演员")
            actor_name ="noactor"
        else:
            actor_name = actor_names[0]
        actor_folder = os.path.join(dir_path, actor_name)
        if not os.path.exists(actor_folder):
            os.makedirs(actor_folder)

        video_folder = os.path.join(actor_folder, video_title)

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

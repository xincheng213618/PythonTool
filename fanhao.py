import os
import re
import shutil
import filecmp
import requests
from bs4 import BeautifulSoup
import javlibrary
import javdb
import glob
import time

def find_alpha_num_combinations(s):
    pattern = r"(\d{6}-\d{3})"
    matches = re.findall(pattern, s.lower())
    if len(matches) == 1:
        return matches

    pattern = r"(FC2-)(?:PPV-)(\d+)"
    match = re.search(pattern, s.lower())
    if match:
        result = match.group(1) + match.group(2)
        return [result]

    matches = re.findall(r'([A-Za-z]+)[^\w]*(\d+)', s)
    separated = ['{}-{}'.format(match[0], match[1]) for match in matches]

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
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    filename = filename.replace('\n', '').replace('\r', '')
    filename = filename[:255]
    return filename

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

dir_path = r"D:\\"
fanhao_dir_paths = os.listdir(dir_path)
extera_path = os.path.join(dir_path, "Extera")
if not os.path.exists(extera_path):
    os.makedirs(extera_path)

for item in fanhao_dir_paths:
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

    for letter in mark:
        if letter in ["SIS-001", "hhd-800", "com-300"]:
            print(f"过滤 {letter}")
            continue
        print(f"entries：{full_path}  mark：{mark}")
        time.sleep(5)
        videoinfo = javdb.getletterinfo(letter)
        print(videoinfo)

        if not videoinfo:
            print(f"videoinfo为空，移动文件夹 {full_path} 到 {extera_path}")
            shutil.move(full_path, os.path.join(extera_path, item))
            continue

        video_title = videoinfo.get("video_title")
        if not video_title:
            print("找不到title")
            break
        video_title = sanitize_filename(video_title)

        actor_names = videoinfo.get("actor_names", [])
        if not actor_names:
            print("没有演员")
            continue

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

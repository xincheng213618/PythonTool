import stat
import rarfile
import zipfile
import py7zr
import os
import subprocess
import shutil
import argparse
import json
import csv
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

dir_path = r'H:\新建文件夹\341'  # 填写你的.rar文件路径
cache_path = r"D:\Cache"
r_path = r"H:\新建文件夹 (3)"
password = 'www.5280bt.net'  # 填写RAR文件的密码
config_file = 'config.json'


def extract_7z_with_password(sevenz_filename, file_directory, password):
    with py7zr.SevenZipFile(sevenz_filename, mode='r', password=password) as z:
        z.extractall(file_directory)


def extract_with_winrar_all(zip_file_path, destination_folder, password):
    command = [r'C:\Program Files\WinRAR\WinRAR.exe', 'x', '-ibck', '-y', f'-p{password}', zip_file_path,
               destination_folder]
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print(e.stderr.decode())


def zip_with_winrar_all(folder_path):
    folder_name = os.path.basename(folder_path)
    target_r_path = r_path if os.path.exists(r_path) else os.path.dirname(folder_path)
    rar_file_name = os.path.join(target_r_path, f"{folder_name}.rar")
    command = [r'C:\Program Files\WinRAR\WinRAR.exe', 'a', '-ibck', '-r', '-ep1', rar_file_name, folder_path]
    print("Running command:", ' '.join(command))
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(e.stderr)


def removesomefile(dir_path):
    os.chmod(dir_path, stat.S_IWUSR)
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            file_path = os.path.join(root, file)
            os.chmod(file_path, stat.S_IWUSR)
            if file.endswith('.url') or file.endswith('.txt'):
                os.remove(file_path)
                print(f"Deleted: {file_path}")


def extract_with_winrar(zip_file_path, password):
    absolute_path = os.path.abspath(zip_file_path)
    file_directory = os.path.dirname(absolute_path)
    extract_with_winrar_all(zip_file_path, file_directory, password)


def unzip_dir(dir_path, password):
    all_items = os.listdir(dir_path)
    sevenz_files = [item for item in all_items if item.endswith('.7z')]

    # 并行解压 7z 文件
    with ThreadPoolExecutor(max_workers=8) as executor:  # 你可以调整 max_workers 数目
        future_to_7z = {
            executor.submit(handle_7z_file, os.path.join(dir_path, sevenz_file), password): sevenz_file
            for sevenz_file in sevenz_files
        }
        for future in as_completed(future_to_7z):
            sevenz_file = future_to_7z[future]
            try:
                future.result()
            except Exception as exc:
                print(f"{exc}")


def handle_7z_file(sevenz_file_path, password):
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)

    tempcache = os.path.join(cache_path, os.path.basename(sevenz_file_path))
    print("正在解压" + sevenz_file_path + "到" + tempcache)

    extract_7z_with_password(sevenz_file_path, tempcache, password)

    all_items1 = os.listdir(tempcache)
    zip_files = [item for item in all_items1 if item.endswith('.zip')]

    # 并行解压 zip 文件
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_zip = {
            executor.submit(handle_zip_file, os.path.join(tempcache, zip_file), password, tempcache): zip_file
            for zip_file in zip_files
        }
        for future in as_completed(future_to_zip):
            zip_file = future_to_zip[future]
            try:
                future.result()
            except Exception as exc:
                print(f"{zip_file} generated an exception: {exc}")


    print("正在删除handle_7z_file" + sevenz_file_path)
    os.remove(sevenz_file_path)
    print("正在删除htempcache" + tempcache)
    shutil.rmtree(tempcache)

def handle_zip_file(zip_file_path, password, tempcache):
    print("正在解压" + zip_file_path)
    extract_with_winrar(zip_file_path, password)
    entries = os.listdir(tempcache)
    directories = [entry for entry in entries if os.path.isdir(os.path.join(tempcache, entry))]

    for directory in directories:
        process_and_compress_dir(os.path.join(tempcache, directory));

    print("正在删除handle_zip_file" + zip_file_path)
    os.remove(zip_file_path)


def process_and_compress_dir(directory_path):
    print(directory_path)
    removesomefile(directory_path)
    zip_with_winrar_all(directory_path)
    print("正在删除process_and_compress_dir" + directory_path)
    shutil.rmtree(directory_path)


def read_config():
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return {}


def write_config(config):
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)


def load_csv_to_dict(file_path):
    data_dict = {}
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            if len(row) < 2:
                continue
            entry_title = row[2]
            path = row[4]
            data_dict[entry_title] = path
    return data_dict


def find_gril_nums_path(data_dict, num):
    # 将 num 转为字符串，左侧补零到3位
    num_str = f"{int(num):03d}"
    pattern = re.compile(rf"B{num_str}")
    for entry_title, path in data_dict.items():
        if pattern.match(entry_title):
            return path
    return ""


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process a directory path.")
    parser.add_argument('-dir_path', "-i",
                        help='The path to the directory.')
    parser.add_argument('-r_path', "-o",
                        help='The path to the directory.')
    args = parser.parse_args()
    print(args)
    config = read_config()
    dir_path = args.dir_path
    r_path = args.r_path

    file_path = 'artfilepath.csv'
    data_dict = load_csv_to_dict(file_path)
    print(data_dict)
    file_name = os.path.basename(dir_path)
    print(file_name)
    if r_path is None and dir_path in config:
        r_path = config[dir_path]
    elif file_name.isdigit() and (0 <= int(file_name) <= 1000):
        print(file_name)
        r_path = find_gril_nums_path(data_dict, int(file_name))
    elif r_path is None:
        parser.error("r_path is required.")
    config[dir_path] = r_path
    write_config(config)

    print("dir_path: " + str(dir_path))
    if not os.path.exists(cache_path):
        cache_path = os.path.join(os.path.expanduser("~"), 'Desktop') + "\Cache"
        if not os.path.exists(cache_path):
            os.makedirs(cache_path)
    cache_path = os.path.join(cache_path, os.path.basename(dir_path))
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)
    print("cache_path:" + cache_path)
    print("r_path:" + r_path)
    if not os.path.exists(r_path):
        os.makedirs(r_path)

    unzip_dir(dir_path, password)

    entries = os.listdir(dir_path)
    directories = [entry for entry in entries if os.path.isdir(os.path.join(dir_path, entry))]
    for directory in directories:
        directory_path = os.path.join(dir_path, directory)
        print(directory_path)
        unzip_dir(directory_path, password)

    print("解压完成，正在清理缓存文件夹:" + cache_path)
    shutil.rmtree(cache_path)
    print("解压完成，正在清理wancheg文件夹:" + dir_path)
    shutil.rmtree(dir_path)

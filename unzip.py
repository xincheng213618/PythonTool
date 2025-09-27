import stat
import rarfile
import zipfile
import py7zr
import os
import subprocess
import shutil
import argparse
import csv
import re
import time
import uuid
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed



# 已移除 config_file 及相关配置持久化逻辑，只保留 CSV 映射

def open_output_folder(path: str):
    try:
        if not os.path.isdir(path):
            print(f"输出目录不存在: {path}")
            return
        if os.name == 'nt':  # Windows
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == 'darwin':  # macOS
            subprocess.Popen(['open', path])
        else:  # Linux/Unix
            subprocess.Popen(['xdg-open', path])
        print(f"已打开输出目录: {path}")
    except Exception as e:
        print(f"打开输出目录失败: {e}")


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
    target_r_path = output_path if os.path.exists(output_path) else os.path.dirname(folder_path)
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


def unzip_dir(input_path, password):
    all_items = os.listdir(input_path)
    sevenz_files = [item for item in all_items if item.endswith('.7z')]

    # 并行解压 7z 文件
    with ThreadPoolExecutor(max_workers=8) as executor:  # 你可以调整 max_workers 数目
        future_to_7z = {
            executor.submit(handle_7z_file, os.path.join(input_path, sevenz_file), password): sevenz_file
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

    # 并行解压 zip 文件，每个zip解压到独立子目录
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_zip = {}
        for zip_file in zip_files:
            zip_file_path = os.path.join(tempcache, zip_file)
            zip_name_no_ext = os.path.splitext(zip_file)[0]
            zip_extract_dir = os.path.join(tempcache, zip_name_no_ext)
            if not os.path.exists(zip_extract_dir):
                os.makedirs(zip_extract_dir)
            future = executor.submit(handle_zip_file, zip_file_path, password, zip_extract_dir)
            future_to_zip[future] = zip_file
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

def handle_zip_file(zip_file_path, password, extract_dir):
    print("正在解压" + zip_file_path + " 到 " + extract_dir)
    extract_with_winrar_all(zip_file_path, extract_dir, password)
    entries = os.listdir(extract_dir)
    directories = [entry for entry in entries if os.path.isdir(os.path.join(extract_dir, entry))]

    for directory in directories:
        process_and_compress_dir(os.path.join(extract_dir, directory))

    print("正在删除handle_zip_file" + zip_file_path)
    os.remove(zip_file_path)


def process_and_compress_dir(directory_path):
    print(directory_path)
    removesomefile(directory_path)
    zip_with_winrar_all(directory_path)
    print("正在删除process_and_compress_dir" + directory_path)
    shutil.rmtree(directory_path)


def load_csv_to_dict(file_path):
    data_dict = {}
    if not os.path.exists(file_path):
        print(f"CSV文件不存在: {file_path}")
        return data_dict
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        import csv as _csv
        csvreader = _csv.reader(csvfile)
        for row in csvreader:
            if len(row) < 5:  # 修正索引越界
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


def is_numeric_dir_name(name: str) -> bool:
    return name.isdigit() and 0 <= int(name) <= 1000


def process_single_folder(single_input_path: str, mapped_output_path: str, password: str):
    """处理单个数字目录：建立独立 cache, 设置全局 output_path/cache_path, 执行解压与清理并删除源目录。"""
    global output_path, cache_path
    output_path = mapped_output_path  # 供 zip_with_winrar_all 使用

    # 独立缓存目录（含时间戳+随机后缀）
    desktop = os.path.join(os.path.expanduser("~"), 'Desktop')
    unique_suffix = f"{int(time.time())}_{uuid.uuid4().hex[:6]}"
    cache_dir_name = f"{os.path.basename(single_input_path)}_{unique_suffix}"
    cache_path = os.path.join(desktop, 'Cache', cache_dir_name)
    os.makedirs(cache_path, exist_ok=True)

    print(f"开始处理目录: {single_input_path} -> {output_path}")
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    unzip_dir(single_input_path, password)

    entries = os.listdir(single_input_path)
    directories = [entry for entry in entries if os.path.isdir(os.path.join(single_input_path, entry))]
    for directory in directories:
        directory_path = os.path.join(single_input_path, directory)
        print(directory_path)
        unzip_dir(directory_path, password)

    print("解压完成，正在清理缓存文件夹:" + cache_path)
    if os.path.exists(cache_path) and len(cache_path) > 10 and 'Cache' in cache_path:
        shutil.rmtree(cache_path)

    # 始终删除源目录（安全校验）
    print("解压完成，正在清理源目录:" + single_input_path)
    if os.path.exists(single_input_path) and len(single_input_path) > 10 and os.path.basename(single_input_path) != '' and single_input_path not in ['/', 'C:\\']:
        shutil.rmtree(single_input_path)
    else:
        print(f"跳过删除源目录: {single_input_path}")

    open_output_folder(output_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process a directory path.")
    parser.add_argument('-i', '--input_path', default="H:\\", help='输入目录（input directory）')
    parser.add_argument('-o', '--output_path', help='输出目录（output directory）')
    parser.add_argument('-p', '--password', default="www.5280bt.net")

    args = parser.parse_args()
    print(args)

    input_path = args.input_path
    output_path = args.output_path  # 可能在 batch 模式中被覆盖
    password = args.password

    file_path = 'artfilepath.csv'
    data_dict = load_csv_to_dict(file_path)

    if not os.path.isdir(input_path):
        parser.error(f"输入路径不是目录: {input_path}")

    file_name = os.path.basename(os.path.normpath(input_path))

    numeric_subdirs = [d for d in os.listdir(input_path) if os.path.isdir(os.path.join(input_path, d)) and is_numeric_dir_name(d)]
    batch_mode = not is_numeric_dir_name(file_name) and len(numeric_subdirs) > 0 and output_path is None

    if batch_mode:
        print(f"检测到批量模式，发现 {len(numeric_subdirs)} 个数字子目录。")
        for d in sorted(numeric_subdirs, key=lambda x: int(x)):
            mapped = find_gril_nums_path(data_dict, int(d))
            if not mapped:
                print(f"跳过 {d}：CSV 未找到映射。")
                continue
            single_input = os.path.join(input_path, d)
            process_single_folder(single_input, mapped, password)
        print("批量任务完成。")
        sys.exit(0)

    if output_path is None:
        if is_numeric_dir_name(file_name):
            mapped = find_gril_nums_path(data_dict, int(file_name))
            if mapped:
                output_path = mapped
            else:
                parser.error(f"CSV 中未找到对应编号 {file_name} 的输出路径")
        else:
            parser.error("未指定 -o 且文件夹名不是有效数字编号，无法确定输出目录")

    desktop = os.path.join(os.path.expanduser("~"), 'Desktop')
    unique_suffix = f"{int(time.time())}_{uuid.uuid4().hex[:6]}"
    cache_dir_name = f"{os.path.basename(input_path)}_{unique_suffix}" if os.path.basename(input_path) else unique_suffix
    cache_path = os.path.join(desktop, 'Cache', cache_dir_name)
    os.makedirs(cache_path, exist_ok=True)

    print("input_path: " + str(input_path))
    print("cache_path:" + cache_path)
    print("r_path:" + output_path)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    unzip_dir(input_path, password)

    entries = os.listdir(input_path)
    directories = [entry for entry in entries if os.path.isdir(os.path.join(input_path, entry))]
    for directory in directories:
        directory_path = os.path.join(input_path, directory)
        print(directory_path)
        unzip_dir(directory_path, password)

    print("解压完成，正在清理缓存文件夹:" + cache_path)
    if os.path.exists(cache_path) and len(cache_path) > 10 and 'Cache' in cache_path:
        shutil.rmtree(cache_path)
    else:
        print(f"跳过删除cache_path: {cache_path}")

    # 始终删除输入源目录（安全校验）
    print("解压完成，正在清理源目录:" + input_path)
    if os.path.exists(input_path) and len(input_path) > 10 and os.path.basename(input_path) != '' and input_path not in ['/', 'C:\\']:
        shutil.rmtree(input_path)
    else:
        print(f"跳过删除input_path: {input_path}")

    open_output_folder(output_path)

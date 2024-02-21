# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。
import rarfile
import zipfile
import py7zr
import os

dir_path = r'H:\新建文件夹\341'  # 填写你的.rar文件路径
cache_path = "D:\Cache"
r_path = r"H:\新建文件夹 (3)"
password = 'www.5280bt.net'  # 填写RAR文件的密码

def extract_rar_with_password(rar_path,file_directory, password):
    with rarfile.RarFile(rar_path) as rf:
        rf.setpassword(password)
        rf.extractall(file_directory)


def extract_zip_with_password(zip_file_path, password):
    with zipfile.ZipFile(zip_file_path) as zip_ref:
        zip_ref.setpassword(password.encode())
        zip_ref.extractall(os.path.dirname(zip_file_path))

def extract_7z_with_password(sevenz_filename, file_directory,password):
    with py7zr.SevenZipFile(sevenz_filename, mode='r', password=password) as z:
        z.extractall(file_directory)


import subprocess
def extract_with_winrar_all(zip_file_path, destination_folder, password):
    # 构建WinRAR命令行指令
    # 注意：命令中的 "x" 表示解压缩并保留目录结构
    # "-ibck" 参数使WinRAR在后台运行
    # "-y" 参数表示不提示确认
    # "-p" 后跟密码用于解压带密码的文件
    command = [r'C:\Program Files\WinRAR\WinRAR.exe', 'x', '-ibck', '-y', f'-p{password}', zip_file_path, destination_folder]
    # 运行命令
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # 输出WinRAR的输出信息
        print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        # 如果有错误发生，输出错误信息
        print(e.stderr.decode())


def zip_with_winrar_all(folder_path):
    # 从文件夹路径获取文件夹名称
    folder_name = os.path.basename(folder_path)

    if os.path.exists(r_path):
        rar_file_name = os.path.join(r_path, f"{folder_name}.rar");
    else:
        rar_file_name = os.path.join(os.path.dirname(folder_path), f"{folder_name}.rar");

    # 压缩文件的名称与文件夹名称相同

    # 完整的WinRAR命令
    command = [r'C:\Program Files\WinRAR\WinRAR.exe', 'a', '-ibck', '-r','-ep1' ,rar_file_name, folder_path]

    # 打印命令，检查是否正确
    print("Running command:", ' '.join(command))

    # 运行命令
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # 输出WinRAR的输出信息
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        # 如果有错误发生，输出错误信息
        print(e.stderr)



def extract_with_winrar(zip_file_path, password):
    absolute_path = os.path.abspath(zip_file_path)
    file_directory = os.path.dirname(absolute_path)
    extract_with_winrar_all(zip_file_path,file_directory, password);
# 使用示例

def removesomefile(dir_path):
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            file_path = os.path.join(root, file)
            os.chmod(file_path, stat.S_IWUSR)
            # 检查文件扩展名是否为.url或.txt
            if file.endswith('.url') or file.endswith('.txt'):
                # 构造文件的完整路径
                # 删除文件
                os.remove(file_path)
                print(f"Deleted: {file_path}")

import shutil

def unzip_dir(dir_path,password):
    all_items = os.listdir(dir_path)
    sevenz_files = [item for item in all_items if item.endswith('.7z')]
    # 遍历所有.7z文件并解压
    for sevenz_file in sevenz_files:
        sevenz_file_path = os.path.join(dir_path, sevenz_file)
        if os.path.exists(cache_path):
            print("正在解压" + sevenz_file_path + "到" +cache_path)
            extract_7z_with_password(sevenz_file_path, cache_path, password)
            all_items1 = os.listdir(cache_path)
            zip_files = [item for item in all_items1 if item.endswith('.zip')]
            for zip_file in zip_files:
                zip_file_path = os.path.join(cache_path, zip_file)
                print("正在解压" + zip_file_path)
                extract_with_winrar(zip_file_path, password)
                # 获取当前目录下的所有条目
                entries = os.listdir(cache_path)

                directories = [entry for entry in entries if os.path.isdir(os.path.join(cache_path, entry))]
                for directory in directories:
                    directory_path = os.path.join(cache_path, directory)
                    print(directory_path)
                    removesomefile(directory_path)
                    
                    
                    
                    zip_with_winrar_all(directory_path);
                    print("正在删除" + directory_path)
                    shutil.rmtree(directory_path)
                print("正在删除" + zip_file_path)
                os.remove(zip_file_path)
        else:
            file_directory = os.path.dirname(sevenz_file_path)
            extract_7z_with_password(sevenz_file_path,file_directory, password)
            # 更新文件列表，以便搜索新解压出的.rar文件
            all_items1 = os.listdir(dir_path)
            zip_files = [item for item in all_items1 if item.endswith('.zip')]
            for zip_file in zip_files:
                zip_file_path = os.path.join(dir_path, zip_file)
                print(zip_file_path)
                extract_with_winrar(zip_file_path, password)
                # 获取当前目录下的所有条目
                entries = os.listdir(dir_path)

                directories = [entry for entry in entries if os.path.isdir(os.path.join(dir_path, entry))]
                for directory in directories:
                    directory_path = os.path.join(dir_path, directory)
                    removesomefile(directory_path)
                    zip_with_winrar_all(directory_path);
                    shutil.rmtree(directory_path)
                os.remove(zip_file_path)

        print("正在删除" + sevenz_file_path)
        os.remove(sevenz_file_path)




        # # 筛选出所有以.rar结尾的文件
        # rar_files = [item for item in all_items1 if item.endswith('.rar')]
        # print(rar_files)
        #
        # # 遍历所有.rar文件并解压
        # for rar_file in rar_files:
        #     rar_file_path = os.path.join(dir_path, rar_file)
        #     print(rar_file_path)
        #     file_directory = os.path.dirname(rar_file_path)
        #     if os.path.exists(cache_path):
        #         file_directory = cache_path
        #     extract_rar_with_password(rar_file_path,file_directory,password)




import argparse
# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':

    # 创建 ArgumentParser 对象
    parser = argparse.ArgumentParser(description="Process a directory path.")

    # 添加 dir_path 参数
    # nargs='?' 表示参数是可选的，const 表示如果没有提供参数，则使用这个默认值
    # type=lambda x: 是一个检查路径是否存在的函数
    parser.add_argument('-dir_path',"-d",type=lambda x: os.path.isdir(x) and x or parser.error("Directory does not exist."), default=r"H:\新建文件夹\319",
                        help='The path to the directory.')

    parser.add_argument('-r_path',"-r",type=lambda x: os.path.isdir(x) and x or parser.error("Directory does not exist."), default=r"H:\新建文件夹 (3)",
                        help='The path to the directory.')

    # 解析命令行参数
    args = parser.parse_args()

    dir_path = args.dir_path
    print("dir_path" + str(dir_path))
    if not os.path.exists(cache_path):
        cache_path = os.path.join(os.path.expanduser("~"), 'Desktop') +"\Cache"
        if not os.path.exists(cache_path):
            os.makedirs(cache_path)

    cache_path =os.path.join(cache_path,os.path.basename(dir_path))
    if not os.path.exists(cache_path):  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(cache_path)  # makedirs 创建文件时如果路径不存在会创建这个路径

    print("cache_path:"+cache_path)

    r_path = args.r_path
    # r_path =os.path.join(r_path,os.path.basename(dir_path))
    # if not os.path.exists(r_path): os.makedirs(r_path)

    print("r_path:"+r_path)

    unzip_dir(dir_path, password)
    entries = os.listdir(dir_path)
    directories = [entry for entry in entries if os.path.isdir(os.path.join(dir_path, entry))]
    for directory in directories:
        directory_path = os.path.join(dir_path, directory)
        print(directory_path)
        unzip_dir(directory_path, password)

    print("解压完成，正在清理缓存文件夹:" +cache_path)
    shutil.rmtree(cache_path)
    print("解压完成，正在清理wancheg文件夹:" +dir_path)
    shutil.rmtree(dir_path)






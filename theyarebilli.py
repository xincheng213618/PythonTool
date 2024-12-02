import os
import zipfile
import shutil
from datetime import datetime
import time

# 源文件夹路径
source_folder = r'C:\Users\17917\Documents\My Games\They Are Billions'
# 目标文件夹路径
backup_folder = r'C:\Users\17917\Documents\My Games'


def backup_folder_to_zip(source, destination):
    # 获取当前时间戳
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    # 压缩文件的名称
    zip_filename = os.path.join(destination, f'TheyAreBillionsBackup_{timestamp}.zip')

    # 创建压缩文件
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 遍历源文件夹
        for foldername, subfolders, filenames in os.walk(source):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                # 将文件添加到zip中，并保留相对路径
                arcname = os.path.relpath(file_path, source)
                zipf.write(file_path, arcname)


while True:
    backup_folder_to_zip(source_folder, backup_folder)
    print(f"Backup completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    # 等待60秒再进行下一次备份
    time.sleep(60)
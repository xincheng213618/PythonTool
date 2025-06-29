import os
import shutil
import sys

def is_hidden_or_system(folder_name):
    return (folder_name == "System Volume Information" or folder_name.startswith('.'))

def main(drive):
    root = os.path.abspath(drive)
    target_folder = os.path.join(root, "[一本专属]")
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    for folder in os.listdir(root):
        abs_folder = os.path.join(root, folder)
        # 只处理一级目录，且排除系统和隐藏文件夹
        if not os.path.isdir(abs_folder):
            continue
        if is_hidden_or_system(folder) or folder == "[一本专属]":
            continue

        # 获取一级目录下内容
        sub_items = [f for f in os.listdir(abs_folder) if not is_hidden_or_system(f)]
        sub_dirs = [f for f in sub_items if os.path.isdir(os.path.join(abs_folder, f))]
        # 只有一个子文件夹且没有其它文件
        if len(sub_dirs) == 1 and len(sub_items) == 1:
            only_subdir = sub_dirs[0]
            src = os.path.join(abs_folder, only_subdir)
            dst = os.path.join(target_folder, only_subdir)
            print(f"Moving {src} -> {dst}")
            if os.path.exists(dst):
                print(f"目标已存在：{dst}，跳过")
                continue
            shutil.move(src, dst)

if __name__ == "__main__":
    drivr ="O:\\"
    main(drivr)
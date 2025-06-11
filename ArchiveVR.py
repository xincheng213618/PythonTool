import os
import shutil
import stat


class FileMover:
    def __init__(self, root_dirs,target_roots):
        self.root_dirs = root_dirs
        self.target_roots = target_roots


    def is_hidden(self, filepath):
        """Check if a file is hidden."""
        return bool(os.stat(filepath).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)

    def remove_empty_dirs(self, path):
        """Recursively remove empty directories."""
        if not os.path.isdir(path):
            return

        # Remove all empty subdirectories
        for root, dirs, files in os.walk(path, topdown=False):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                try:
                    os.rmdir(dir_path)
                    print(f"Removed empty directory: {dir_path}")
                except OSError:
                    # Directory is not empty
                    pass

        # Remove the root directory if it's empty
        try:
            os.rmdir(path)
            print(f"Removed empty directory: {path}")
        except OSError:
            # Directory is not empty
            pass

    def move_files(self):
        print(self.root_dirs)

        # 从后往前遍历根目录
        for i in range(len(self.root_dirs) - 1, 0, -1):
            root_dir = self.root_dirs[i]
            # 获取需要输出的前面根目录
            target_roots = self.target_roots
            for folder_name in os.listdir(root_dir):
                try:
                    folder_path = os.path.join(root_dir, folder_name)
                    print(f"Moving folder: {folder_name}")
                    # 检查这是一个文件夹
                    if os.path.isdir(folder_path) and not self.is_hidden(folder_path):

                        # 找到第一个存在对应文件夹的目标根目录
                        target_root = None
                        for tr in target_roots:
                            target_folder_path = os.path.join(tr, folder_name)
                            if os.path.exists(target_folder_path):
                                target_root = tr
                                break

                        if target_root is None:
                            print(f"No target folder found for: {folder_path}")
                            continue

                        target_folder_path = os.path.join(target_root, folder_name)
                        print(f"Moving contents from {folder_path} to {target_folder_path}")

                        # 遍历源目录中的所有文件和文件夹
                        for item in os.listdir(folder_path):
                            source_item = os.path.join(folder_path, item)
                            target_item = os.path.join(target_folder_path, item)

                            # 跳过隐藏的文件或文件夹
                            if self.is_hidden(source_item):
                                print(f"Skipping hidden item: {source_item}")
                                continue

                            if ("DVRT" in source_item):
                                continue

                            if ("VR" not in source_item):
                                continue

                            print("move",source_item, "to",target_item)

                            # 如果是文件，直接移动并覆盖
                            if os.path.isfile(source_item):
                                print(f"Moving file: {source_item} to {target_item}")
                                shutil.move(source_item, target_item)

                            # 如果是文件夹，需要逐个文件移动
                            elif os.path.isdir(source_item):
                                # 如果目标文件夹不存在，直接移动
                                if not os.path.exists(target_item):
                                    print(f"Moving folder: {source_item} to {target_item}")
                                    shutil.move(source_item, target_item)
                                else:
                                    # 如果目标文件夹存在，合并文件夹内容
                                    for sub_root, dirs, files in os.walk(source_item):
                                        # 跳过隐藏的文件夹
                                        if self.is_hidden(sub_root):
                                            print(f"Skipping hidden folder: {sub_root}")
                                            continue
                                        # 计算相对路径以构建目标路径
                                        rel_path = os.path.relpath(sub_root, source_item)
                                        target_sub_root = os.path.join(target_item, rel_path)
                                        # 创建文件夹
                                        os.makedirs(target_sub_root, exist_ok=True)
                                        for file in files:
                                            print(
                                                f"Moving file: {os.path.join(sub_root, file)} to {os.path.join(target_sub_root, file)}")
                                            shutil.move(os.path.join(sub_root, file),
                                                        os.path.join(target_sub_root, file))
                                        # 移动所有子文件夹
                                        for dir in dirs:
                                            print(
                                                f"Moving folder: {os.path.join(sub_root, dir)} to {os.path.join(target_sub_root, dir)}")
                                            shutil.move(os.path.join(sub_root, dir), os.path.join(target_sub_root, dir))

                        # 删除空的源文件夹
                        self.remove_empty_dirs(folder_path)
                except:
                    continue



# 使用示例
if __name__ == "__main__":
    root_dirs = ["V:\\[A]","G:\\","F:\\","O:\\[珍藏]","O:\\","D:\\"]
    target_roots =["V:\\[A]"]
    file_mover = FileMover(root_dirs,target_roots)
    file_mover.move_files()
import os
import shutil
import stat
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

class FileMover:
    def __init__(self, root_dirs):
        self.root_dirs = root_dirs
        self.system_hidden_names = ['system volume information', '$recycle.bin']


    def is_hidden(self, filepath):
        base = os.path.basename(filepath).lower()
        # 过滤以 . 开头的隐藏文件、系统目录
        if base.startswith('.'):
            return True
        if base in self.system_hidden_names:
            return True
        # 检查路径中是否包含系统隐藏目录
        path_lower = filepath.lower()
        for sys_name in self.system_hidden_names:
            if sys_name in path_lower:
                return True
        # Windows 下检查文件属性是否为隐藏
        try:
            attrs = os.stat(filepath).st_file_attributes
            if attrs & stat.FILE_ATTRIBUTE_HIDDEN:
                return True
            if attrs & stat.FILE_ATTRIBUTE_SYSTEM:
                return True
        except Exception:
            pass
        return False

    def remove_empty_dirs(self, path):
        if not os.path.isdir(path):
            return
        for root, dirs, files in os.walk(path, topdown=False):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                try:
                    os.rmdir(dir_path)
                    print(f"Removed empty directory: {dir_path}")
                except OSError:
                    pass
        try:
            os.rmdir(path)
            print(f"Removed empty directory: {path}")
        except OSError:
            pass

    def robocopy_move(self,src, dst):
        # /MOVE 表示移动，/E 包含空目录
        cmd = ["robocopy", src, dst, "/MOVE", "/E"]
        result = subprocess.run(cmd, shell=True)
        if result.returncode >= 8:
            raise RuntimeError("robocopy failed with code %d" % result.returncode)

    def move_diskpair(self, src_root, dst_root):
        for folder_name in os.listdir(src_root):
            if(self.is_hidden(os.path.join(src_root, folder_name))):
                continue
            src_folder = os.path.join(src_root, folder_name)
            dst_folder = os.path.join(dst_root, folder_name)
            if os.path.isdir(src_folder) and not self.is_hidden(src_folder):
                if os.path.exists(dst_folder):
                    print(f"[{src_root}→{dst_root}] Moving contents from {src_folder} to {dst_folder}")
                    for item in os.listdir(src_folder):
                        src_item = os.path.join(src_folder, item)
                        dst_item = os.path.join(dst_folder, item)
                        if self.is_hidden(src_item):
                            continue
                        self.robocopy_move(src_item,dst_item)
                    self.remove_empty_dirs(src_folder)


    def move_files_diskpair_parallel(self):
        tasks = []
        with ThreadPoolExecutor(max_workers=len(self.root_dirs) ** 2) as executor:
            for i, src in enumerate(self.root_dirs):
                for j, dst in enumerate(self.root_dirs):
                    if i > j:  # 只允许“编号靠后的”往“编号靠前的”传
                        tasks.append(executor.submit(self.move_diskpair, src, dst))
            for future in as_completed(tasks):
                future.result()

if __name__ == "__main__":
    root_dirs = ["G:\\", "F:\\","O:\\[珍藏]","O:\\","D:\\"]
    file_mover = FileMover(root_dirs)
    file_mover.move_files_diskpair_parallel()
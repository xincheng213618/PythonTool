import os
import re
import hashlib

def file_hash(path, chunk_size=1024*1024):
    """计算文件的SHA256 hash."""
    h = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                h.update(chunk)
    except Exception as e:
        print(f"Error calculating hash for {path}: {e}")
        return None
    return h.hexdigest()

def delete_matching_files_and_empty_dirs(directory, keywords):
    max_size = 100 * 1024 * 1024  # 100MB
    pattern = re.compile(r'（\d+）')

    for root, dirs, files in os.walk(directory, topdown=False):
        size_to_files = {}
        for file in files:
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                size_to_files.setdefault(size, []).append(file_path)
            except Exception as e:
                print(f"Error getting size for {file_path}: {e}")

        # 删除同目录下重复(hash一致)的文件，只保留一个，优先删带（数字）后缀
        for same_size_files in size_to_files.values():
            if len(same_size_files) > 1:
                hash_to_files = {}
                for f in same_size_files:
                    h = file_hash(f)
                    if h:
                        hash_to_files.setdefault(h, []).append(f)
                for files_with_same_hash in hash_to_files.values():
                    if len(files_with_same_hash) > 1:
                        with_suffix = [f for f in files_with_same_hash if pattern.search(os.path.basename(f))]
                        without_suffix = [f for f in files_with_same_hash if not pattern.search(os.path.basename(f))]
                        files_to_keep = []
                        if without_suffix:
                            without_suffix.sort()
                            files_to_keep.append(without_suffix[0])
                        else:
                            with_suffix.sort()
                            files_to_keep.append(with_suffix[0])
                        files_to_delete = [f for f in files_with_same_hash if f not in files_to_keep]
                        for dup_file in files_to_delete:
                            try:
                                if os.path.exists(dup_file):
                                    os.remove(dup_file)
                                    print(f"Deleted duplicate file: {dup_file}")
                            except Exception as e:
                                print(f"Error deleting duplicate file {dup_file}: {e}")

        # 删除匹配的文件
        for file in files:
            if any(keyword in file for keyword in keywords):
                file_path = os.path.join(root, file)
                try:
                    if os.path.exists(file_path):
                        if os.path.getsize(file_path) <= max_size:
                            os.remove(file_path)
                            print(f"Deleted file: {file_path}")
                        else:
                            print(f"Skipped large file (>100MB): {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")

        # 删除空文件夹
        try:
            if not os.listdir(root):
                os.rmdir(root)
                print(f"Deleted empty directory: {root}")
        except Exception as e:
            print(f"Error deleting directory {root}: {e}")

if __name__ == "__main__":
    directory_to_search = "D:\\"
    keywords_to_match = ["美女荷官","杏吧","社区最新情报","妹妹在精彩表演","manko.fun","sex8.cc","u u r","UUE","offkab@sukebei","tuu32.com","新片首发 每天更新 同步日韩","[资源推荐]！下载地址","#第一会所sis001.com最新地址",".gif","最 新 位 址 獲 取 ","1024草榴社區","2048",".apk","18+游戏大全","x u u ","uur9 3.com","新 片 首 發","有趣的台湾妹妹直播",".chm",".html",".mht",".url","有 趣 的 臺 灣 妹 妹 直 播","1063715@18p2p.com.txt","三 上 悠 亚 想 要 跟 你 决 胜 负","电 竞 直 播 平台"," 福 利 机 置","安卓二维码","最新地址.png","最新地址获取.txt","苍 老 师 强 力 推 荐.mp4","女神在线视频","最新网址","更多高清影片访问","18+游戏大全", "聚 合 全 網 H 直 播", "社 區 最 新 情 報","最 新 位 址 獲 取.txt","台 妹 子 線 上 現 場 直 播 各 式 花 式 表 演.mp4"]  # 修改为你的目标关键字

    delete_matching_files_and_empty_dirs(directory_to_search, keywords_to_match)
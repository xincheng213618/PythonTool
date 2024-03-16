import sys
import os
import sys
import subprocess
import time
import pyautogui

if __name__ == '__main__':
    print("hello world")
    dir_path = r"D:\音乐（无损）"
    all_items1 = os.listdir(dir_path)
    for item in all_items1:
        name_items = os.listdir(dir_path + "\\" + item)
        print(name_items)
        zip_files = [item for item in name_items if item.endswith('.exe')]
        for zip_file in zip_files:
            exe_path = dir_path + "\\" + item + "\\" + zip_file
            print(exe_path)
            subprocess.Popen(exe_path, shell=True)
            print("正在打开" + exe_path)
            time.sleep(1)
            pyautogui.press('enter')
            current_size = os.path.getsize(exe_path)
            ts = int(current_size / 100 / 1024 / 1024) + 1

            print("正在解压" + exe_path + "用时" + str(ts) + "s")

            time.sleep(ts)
            print("正在删除" + exe_path)
            try:
                os.remove(exe_path)
            except:
                time.sleep(5)
                try:
                    os.remove(exe_path)


                except:
                    pyautogui.press('enter')
                    time.sleep(ts)

                    os.remove(exe_path)

            # os.system(dir_path + "\\" + zip_file)

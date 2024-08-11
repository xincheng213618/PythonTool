import tosrt
import translatesrt

with open(r"C:\Users\Chen\Desktop\Cache\slicer_opt1.list", "r",encoding="utf-8") as f:  # 打开文件
    input_data = f.readlines()  # 读取文件

# 转换成 SRT 格式
srt_content = tosrt.convert_to_srt(input_data)

with open('output.srt', 'w', encoding='utf-8') as f:
    f.writelines(srt_content)

translatesrt.traducir_archivo("output.srt")

import os
top =r"C:\Users\Chen\Desktop\Cache\slicer_opt"
for root, dirs, files in os.walk(top, topdown=False):
    for name in files:
        os.remove(os.path.join(root, name))
    for name in dirs:
        os.rmdir(os.path.join(root, name))
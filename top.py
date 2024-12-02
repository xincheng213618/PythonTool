import json
import os
import urllib.parse
from datetime import datetime
import pythoncom
import win32com.client

output_file = '2023top250_movies.html'
directories = ["Q:\\","P:\\"]
cache_file = "file_search_cache.json"


# Load the movie information from the JSON file
with open("2023top250_movies.json", "r", encoding="utf-8") as f:
    movies = json.load(f)

# Extract all the 番号 and their rankings
codes = {movie["title"].split()[0]: movie for movie in movies}
print(codes)

# Define the directories to search

# Cache to store already found files for each 番号

# Load cache if it exists
if os.path.exists(cache_file):
    with open(cache_file, "r", encoding="utf-8") as f:
        found_files = json.load(f)
else:
    found_files = {code: [] for code in codes}


# Function to save cache
def save_cache():
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(found_files, f, ensure_ascii=False, indent=4)



# Function to search for files containing the 番号
def search_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            for code, movie in codes.items():
                try:
                    if code in file and file_path not in found_files[code]:
                        found_files[code].append(file_path)
                except:
                    found_files[code] = []

        # Save cache periodically to avoid data loss
        if sum(len(paths) for paths in found_files.values()) % 100 == 0:
            save_cache()


for directory in directories:
    search_files(directory)
save_cache()

# HTML 头部
html_header = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"><meta name="viewport" content="width=512"><meta name="robots" content="noindex, nofollow"><title>O:\\ - Everything</title>
<link rel="stylesheet" href="/main.css" type="text/css">
<link rel="shortcut icon" href="/favicon.ico" type="image/x-icon">
</head>
<body><center>
<br>
<br>
<a href="/"><img class="logo" src="/Everything.gif" alt="Everything"></a>
<br>
<br>
<form id="searchform" action="/" method="get"><input class="searchbox" style="width:480px" id="search" name="search" type="text" onfocus="this.select()" title="搜索 Everything" value="" autofocus></form>
<table cellspacing="0" width="480px">
<tr><td colspan="3"><p class="indexof">索引 O:\\</p></td></tr>
<tr><td class="updir" colspan="3"><a href="/O%3A/"><img class="icon" src="/updir.gif" alt="">上一目录..</a></td></tr>
<tr><td class="nameheader"><a href="#"><span class="nobr"><nobr>名称<img class="updown" src="/up.gif" alt=""></nobr></span></a></td><td class="sizeheader"><a href="#"><span class="nobr"><nobr>大小</nobr></span></a></td><td class="modifiedheader"><a href="#"><span class="nobr"><nobr>修改日期</nobr></span></a></td></tr>
<tr><td colspan="3" class="lineshadow" height="1"></td></tr>
'''

# HTML 尾部
html_footer = '''
</table>
</center>
</body>
'''

# 生成文件列表的 HTML 部分
html_body = ''
row_classes = ['trdata1', 'trdata2']
row_class_index = 0

for code, paths in found_files.items():
    for path in paths:
        file_size = os.path.getsize(path)
        file_mtime = os.path.getmtime(path)
        file_url = urllib.parse.quote(path.replace('\\', '/'))
        file_name = os.path.basename(path)

        # 格式化文件大小
        file_size_kb = file_size // 1024

        # 格式化修改时间
        file_mtime_str = datetime.fromtimestamp(file_mtime).strftime('%Y/%m/%d %H:%M')

        # 生成 HTML 行
        html_body += f'''
<tr class="{row_classes[row_class_index]}"><td class="file"><span class="nobr"><nobr><a href="/{file_url}"><img class="icon" src="/file.gif" alt="">{file_name}</a></nobr></span></td><td class="sizedata"><span class="nobr"><nobr>{file_size_kb} KB</nobr></span></td><td class="modifieddata"><span class="nobr"><nobr>{file_mtime_str}</nobr></span></td></tr>
'''
        row_class_index = 1 - row_class_index

# 生成完整的 HTML 内容
html_content = html_header + html_body + html_footer

# 写入 HTML 文件
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f'HTML 文件已生成: {output_file}')

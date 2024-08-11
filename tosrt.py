import re
import re
frame_rate = 3200*10
def frames_to_timestamp(frames):
    # 将时间戳从毫秒转换为 SRT 时间格式（HH:MM:SS,ms）
    dd =  int(frames) / frame_rate
    print(dd)
    hours, remainder = divmod(int(dd), 3600)
    minutes, remainder = divmod(remainder, 60)
    seconds, milliseconds = divmod(remainder, 1)
    milliseconds = int(milliseconds * 1000)  # 转换为毫秒
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def process_line(line):
    print(line)
    # 使用正则表达式提取时间戳和文本内容
    match = re.match(r".*?(\d+)_(\d+)\.wav\|.*?\|JA\|(.*)", line)
    if match:
        start_ts, end_ts, text = match.groups()
        return frames_to_timestamp(start_ts), frames_to_timestamp(end_ts), text
    else:
        return None

def convert_to_srt(input_lines):
    # 转换所有行并生成 SRT 字幕格式的内容
    srt_content = []
    index = 1
    for line in input_lines:
        result = process_line(line)
        if result:
            start, end, text = result
            if text.strip():  # 检查 text 是否为空或只包含空白字符
                srt_content.append(f"{index}\n{start} --> {end}\n{text}\n")
                index += 1  # 只有在 text 不为空时，才增加索引
    return srt_content

# 示例数据，这里应该是从文件读取的内容

with open(r"C:\Users\Chen\Desktop\Cache\slicer_opt.list", "r",encoding="utf-8") as f:  # 打开文件
    input_data = f.readlines()  # 读取文件

# 转换成 SRT 格式
srt_content = convert_to_srt(input_data)

with open('output.srt', 'w', encoding='utf-8') as f:
    f.writelines(srt_content)
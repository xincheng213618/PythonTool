import fitz  # PyMuPDF
import httpx
import pandas as pd
import os
from openai import OpenAI

# 定义要提取的信息字段
fields = [

    "Who are the Authors?",
    "Which year does this paper publish?",
    "What are the research Subjects?",
    "What is the sample size of this paper?",
    "Which year(s) of data from the CLHLS does this paper use?",
    "What is the data selection/screening procedure in this paper?",
    "Which scales or specific questions from the CLHLS database does this paper use in its measurements?",
    "What are the results and findings of this paper?",
    "What are the main conclusions of this paper?",
    "What are the limitations (key points) of this paper?",
    "What is the APA 7th edition reference format for this paper?"
]

# 定义一个函数来提取PDF中的文本
def extract_text_from_first_page(pdf_path):
    doc = fitz.open(pdf_path)
    first_page = doc.load_page(0)
    text = first_page.get_text("text")
    return text

# 定义一个函数来解析文本并提取信息
def extract_info_from_text(text):
    info = {}
    for field in fields:
        print(text)
        ans = extract_gpt(f"{field},my paper content as: {text}")
        print(ans)
        info[field] = ans
    return info

import httpx

client = OpenAI(http_client= httpx.Client(proxies="http://127.0.0.1:10809",transport=httpx.HTTPTransport(local_address="0.0.0.0")),api_key="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", base_url="https://api.openai.com/v1/")
def extract_gpt(text):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role":"system","content":text},
        ]
    )
    return completion.choices[0].message.content


# 处理PDF文件目录中的所有文件
pdf_directory = "C:/Users/wrx36/Desktop/OHW"

pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
pdf_files_sorted = sorted(pdf_files, reverse=True)

data = []
for pdf_file in pdf_files_sorted:
    pdf_path = os.path.join(pdf_directory, pdf_file)
    print(f"index of pdf: {pdf_file}")
    text = extract_text_from_first_page(pdf_path)
    print(1)

    info = extract_info_from_text(text)
    print(info)
    info["PDF Filename"] = pdf_file  # 添加PDF文件名
    data.append(info)

# 将提取的信息保存到CSV文件ai
df = pd.DataFrame(data)
df.to_excel("extracted_info.xlsx", index=False, encoding='utf-8')

print("信息提取完成并保存到 extracted_info.xlsx")

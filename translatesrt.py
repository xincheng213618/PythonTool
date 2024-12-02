import os
from googletrans import Translator, LANGUAGES
import re
import pickle

proxies = {
    "http": "http://127.0.0.1:10809",
    "https": "http://127.0.0.1:10809"
}

from httpcore import SyncHTTPProxy

http_proxy = SyncHTTPProxy((b'http', b'127.0.0.1', 10809, b''))
proxies = {'http': http_proxy, 'https': http_proxy}

translator = Translator(proxies=proxies)


class TranslationCache:
    def __init__(self, src, dest):
        self.src = src
        self.dest = dest
        self.cache_file = src + "_" + dest + ".pickle"
        self.cache = self.load_cache()

    def load_cache(self):
        """加载缓存文件，如果文件不存在，则创建一个空的缓存字典"""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'rb') as f:
                return pickle.load(f)
        else:
            return {}

    def get_translation(self, text):
        """从缓存中获取翻译，如果不存在，则进行翻译并保存到缓存中"""
        if text in self.cache:
            return self.cache[text]
        else:
            # 这里应该是进行翻译的代码，例如调用某个翻译API
            # 假设翻译结果存储在变量 translated_text 中
            translated_text = self.translate_text(text)
            self.cache[text] = translated_text
            return translated_text

    def translate_text(self, text):
        translation = translator.translate(text, src=self.src, dest=self.dest)
        print("translator:" + self.src + self.dest + "  " + text + "result" + translation.text)
        return translation.text

    def save_cache(self):
        """将缓存保存到文件中"""
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.cache, f)


def is_timecode_line(line):
    # 使用正则表达式来检查这一行是否是时间代码行
    return re.match(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', line) is not None


def traducir_archivo(archivo_entrada):
    translator = TranslationCache("ja", "zh-cn")

    nombre_archivo = os.path.basename(archivo_entrada)
    output_file_path = archivo_entrada.replace('.srt', '.zh-cn.srt')

    with open(archivo_entrada, 'r', encoding='utf-8') as archivo_entrada:
        lines = archivo_entrada.readlines()

    input_blocks = []
    for line in lines:
        if line.strip().isdigit():  # 检查是否是序号行
            input_blocks.append(line)
        elif is_timecode_line(line.strip()):  # 检查是否是时间代码行
            input_blocks.append(line)
        else:
            result = translator.get_translation(line)
            input_blocks.append(result + "\n\r")

    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.writelines(input_blocks)
    translator.save_cache()


traducir_archivo(r"C:\Users\Chen\Desktop\unzipPicture\output.srt")

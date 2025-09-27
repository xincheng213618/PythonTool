from psd_tools import PSDImage
from PIL import Image
import os

# 路径设置
psb_path = r"D:\BaiduNetdiskDownload\宇宙全景图(eso1242a).psb"
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
bmp_path = os.path.join(desktop, "宇宙全景图(eso1242a).bmp")

# 读取PSB
psd = PSDImage.open(psb_path)
# 合成所有可见层为一张图
composite = psd.composite()

# 保存为BMP
composite.save(bmp_path, format='BMP')
print(f"已导出 BMP 至: {bmp_path}")
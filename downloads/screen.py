import os
import time
import subprocess
import shutil
import zipfile
import numpy as np
from PIL import Image

# ================== 配置区 ==================
DEVICE = "127.0.0.1:7555"

# 最终图片保存目录
FINAL_DIR = r"D:\books\my_book"

# 生成的 CBZ 文件路径
CBZ_PATH = r"D:\books\my_book.cbz"

# 滑动参数（向右翻页）
START_X = 300
START_Y = 800
END_X   = 900
END_Y   = 800
SWIPE_DURATION = 300

WAIT_AFTER_SWIPE = 1.2

# 最后一页判断参数
SIMILARITY_THRESHOLD = 0.99
MAX_SAME_COUNT = 2
# ===========================================

os.makedirs(FINAL_DIR, exist_ok=True)

def adb(cmd):
    subprocess.run(cmd, shell=True, check=True)

def capture_and_pull(remote, local):
    adb(f"adb -s {DEVICE} shell screencap -p {remote}")
    adb(f"adb -s {DEVICE} pull {remote} {local}")
    adb(f"adb -s {DEVICE} shell rm {remote}")  # 删除模拟器截图

def image_similarity(img1, img2):
    a = np.array(img1).astype(np.float32)
    b = np.array(img2).astype(np.float32)
    diff = np.mean(np.abs(a - b))
    return 1.0 - diff / 255.0

index = 1
prev_img = None
same_count = 0

print("🚀 开始自动截图…")

while True:
    filename = f"{index:04}.png"
    remote_path = f"/sdcard/{filename}"
    local_path = os.path.join(FINAL_DIR, filename)

    print(f"📸 第 {index} 页")

    # 截图 → pull → 删除模拟器文件
    capture_and_pull(remote_path, local_path)

    current_img = Image.open(local_path).convert("RGB")

    # 判断是否到最后一页
    if prev_img is not None:
        sim = image_similarity(prev_img, current_img)
        print(f"   相似度: {sim:.4f}")

        if sim >= SIMILARITY_THRESHOLD:
            same_count += 1
            print(f"   ⚠️ 页面未变化 ({same_count})")
        else:
            same_count = 0

        if same_count >= MAX_SAME_COUNT:
            print("✅ 已到最后一页，停止截图")
            break

    prev_img = current_img
    index += 1

    # 翻页
    adb(
        f"adb -s {DEVICE} shell input swipe "
        f"{START_X} {START_Y} {END_X} {END_Y} {SWIPE_DURATION}"
    )

    time.sleep(WAIT_AFTER_SWIPE)

print(f"📄 截图完成，共 {index} 页")
print("📦 正在生成 CBZ…")

# ================== 生成 CBZ ==================
images = sorted(
    f for f in os.listdir(FINAL_DIR)
    if f.lower().endswith(".png")
)

with zipfile.ZipFile(CBZ_PATH, "w", zipfile.ZIP_STORED) as z:
    for img in images:
        z.write(os.path.join(FINAL_DIR, img), arcname=img)

print("📕 CBZ 生成完成：")
print(CBZ_PATH)
print("🎉 全流程完成")

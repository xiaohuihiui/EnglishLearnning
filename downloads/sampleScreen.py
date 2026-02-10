import os
import time
import subprocess
import zipfile
import numpy as np
from PIL import Image
from datetime import datetime
import shutil

# ================= 基本配置 =================
DEVICE = "127.0.0.1:5555"

BASE_DIR = r"D:\books\my_book"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

OUTPUT_DIR = os.path.join(BASE_DIR, timestamp)
os.makedirs(OUTPUT_DIR, exist_ok=True)

CBZ_PATH = os.path.join(
    os.path.dirname(BASE_DIR),
    f"{timestamp}.cbz"
)

SWIPE_RIGHT = (
    "adb -s 127.0.0.1:5555 shell "
    "input swipe 400 480 120 480 500"
)

WAIT = 1.1

# ⚠️ 只用于“怀疑”，不是直接结束
SIM_THRESHOLD = 0.992
MAX_SUSPECT_COUNT = 2
# ============================================

def adb(cmd):
    subprocess.run(cmd, shell=True, check=True)

def capture_and_pull(index):
    name = f"{index:04}.png"
    remote = f"/sdcard/{name}"
    local = os.path.join(OUTPUT_DIR, name)

    adb(f"adb -s {DEVICE} shell screencap -p {remote}")
    adb(f"adb -s {DEVICE} pull {remote} {local}")
    adb(f"adb -s {DEVICE} shell rm {remote}")

    return local

def image_similarity(img1, img2):
    a = np.array(img1).astype("float32")
    b = np.array(img2).astype("float32")
    return 1.0 - np.mean(np.abs(a - b)) / 255.0

# ================= 主流程 =================
print("🚀 自动截图开始（人工兜底版）")

index = 1
prev_img = None
suspect_count = 0

while True:
    if index > 1:
        adb(SWIPE_RIGHT)
        time.sleep(WAIT)

    print(f"\n📸 第 {index} 页")
    img_path = capture_and_pull(index)
    cur_img = Image.open(img_path).convert("RGB")

    if prev_img is not None:
        sim = image_similarity(prev_img, cur_img)
        print(f"   相似度: {sim:.4f}")

        if sim >= SIM_THRESHOLD:
            suspect_count += 1
            print(f"   ⚠️ 疑似未翻页（连续 {suspect_count} 次）")
        else:
            suspect_count = 0

        # ====== 只在这里打断你 ======
        if suspect_count >= MAX_SUSPECT_COUNT:
            print("\n❓ 程序判断：可能已经是最后一页")
            ans =\
                input("👉 确认已到最后一页？(n=结束 / 回车=继续): ").strip().lower()


            if ans in ("n", "yes"):
                print("➡️ 忽略判断，继续翻页")
                suspect_count = 0
            else:
                print("📕 人工确认结束")
                break


    prev_img = cur_img
    index += 1

print("\n📦 正在生成 CBZ…")

with zipfile.ZipFile(CBZ_PATH, "w", zipfile.ZIP_STORED) as z:
    for f in sorted(os.listdir(OUTPUT_DIR)):
        if f.lower().endswith(".png"):
            z.write(os.path.join(OUTPUT_DIR, f), f)

print("📕 CBZ 生成完成：")
print(CBZ_PATH)

# ===== 安全删除 =====
if os.path.exists(CBZ_PATH) and os.path.getsize(CBZ_PATH) > 0:
    shutil.rmtree(OUTPUT_DIR)
    print(f"🗑️ 已删除截图目录：{OUTPUT_DIR}")
else:
    print("⚠️ CBZ 异常，未删除截图目录")

print("🎉 全流程结束")

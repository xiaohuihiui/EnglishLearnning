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
BASE_DIR = r"E:\books\my_book"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

OUTPUT_DIR = os.path.join(BASE_DIR, timestamp)
os.makedirs(OUTPUT_DIR, exist_ok=True)

CBZ_PATH = os.path.join(
    os.path.dirname(BASE_DIR),
    f"{timestamp}.cbz"
)

SWIPE_RIGHT = (
    f"adb -s {DEVICE} shell "
    "input swipe 400 480 120 480 500"
)

WAIT = 1.16

# ⚠️ 只用于“怀疑”，不是直接结束
SIM_THRESHOLD = 0.992
MAX_SUSPECT_COUNT = 2

# ================= 功能函数 =================

def adb(cmd):
    """
    执行ADB命令，包含自动重连逻辑
    """
    max_retries = 3
    for i in range(max_retries):
        try:
            # 执行命令并捕获错误输出
            return subprocess.run(cmd, shell=True, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            if i < max_retries - 1:
                print(f"\n[!] ADB 连接中断，正在尝试重连 ({i + 1}/{max_retries})...")
                # 强制刷新连接
                subprocess.run(f"adb disconnect {DEVICE}", shell=True, capture_output=True)
                time.sleep(1)
                subprocess.run(f"adb connect {DEVICE}", shell=True, capture_output=True)
                time.sleep(1)
                continue
            else:
                print(f"\n[❌] 无法恢复连接: {cmd}")
                raise e

def capture_and_pull(index):
    """
    截图并拉取到本地
    """
    name = f"{index:04}.png"
    remote = f"/sdcard/{name}"
    local = os.path.join(OUTPUT_DIR, name)

    adb(f"adb -s {DEVICE} shell screencap -p {remote}")
    adb(f"adb -s {DEVICE} pull {remote} \"{local}\"")
    adb(f"adb -s {DEVICE} shell rm {remote}")

    return local

def image_similarity(img1, img2):
    """
    计算两张图片的相似度
    """
    a = np.array(img1).astype("float32")
    b = np.array(img2).astype("float32")
    return 1.0 - np.mean(np.abs(a - b)) / 255.0

# ================= 主流程 =================

def main():
    print("🚀 自动截图开始（含自动断线重连）")

    index = 1
    prev_img = None
    suspect_count = 0

    # 运行前先确保连接一次
    subprocess.run(f"adb connect {DEVICE}", shell=True, capture_output=True)

    while True:
        try:
            if index > 1:
                adb(SWIPE_RIGHT)
                time.sleep(WAIT)

            print(f"\n📸 第 {index} 页", end="", flush=True)
            img_path = capture_and_pull(index)
            cur_img = Image.open(img_path).convert("RGB")

            if prev_img is not None:
                sim = image_similarity(prev_img, cur_img)
                print(f" | 相似度: {sim:.4f}")

                if sim >= SIM_THRESHOLD:
                    suspect_count += 1
                    print(f"   ⚠️ 疑似未翻页（连续 {suspect_count} 次）")
                else:
                    suspect_count = 0

                # ====== 判停逻辑 ======
                if suspect_count >= MAX_SUSPECT_COUNT:
                    print("\n❓ 程序判断：可能已经是最后一页")
                    ans = input("👉 确认已到最后一页？(回车=结束 / n=继续翻页): ").strip().lower()

                    if ans == "n":
                        print("➡️ 忽略判断，继续翻页")
                        suspect_count = 0
                    else:
                        print("📕 人工确认结束")
                        break

            prev_img = cur_img
            index += 1

        except Exception as e:
            print(f"\n[!] 循环过程中出现不可恢复错误: {e}")
            print("[*] 尝试保存已有进度...")
            break

    print("\n📦 正在生成 CBZ…")

    # 检查是否有图片生成
    if os.path.exists(OUTPUT_DIR) and os.listdir(OUTPUT_DIR):
        with zipfile.ZipFile(CBZ_PATH, "w", zipfile.ZIP_STORED) as z:
            files = sorted(os.listdir(OUTPUT_DIR))
            for f in files:
                if f.lower().endswith(".png"):
                    z.write(os.path.join(OUTPUT_DIR, f), f)

        print(
            f"📕 CBZ 生成完成：\n{CBZ_PATH}")

        # ===== 安全删除 =====
        if os.path.exists(CBZ_PATH) and os.path.getsize(CBZ_PATH) > 0:
            shutil.rmtree(OUTPUT_DIR)
            print("🗑️ 已删除临时截图目录")

        else:
            print("⚠️ CBZ 文件异常，保留截图目录供检查")
    else:
        print("❌ 没有截图被生成，跳过 CBZ 制作")

    print("🎉 全流程结束")

if __name__ == "__main__":
    main()
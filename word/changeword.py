import os
import glob
import time
import warnings
import cv2
from PIL import Image

# 1. 屏蔽非致命的系统与框架警告，保持控制台干净
warnings.filterwarnings("ignore", category=UserWarning)

import easyocr


def preprocess_image(img_path):
    """
    对图片进行图像预处理，以增强文字边缘、提高 OCR 准确率
    """
    # 读取图片（包含中文路径处理兼容）
    img = cv2.imread(img_path)
    if img is None:
        return img_path

    # 转为灰度图，消除颜色背景噪音
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 放大图片至 1.5 倍（极大改善小字、脚标及细微印刷体的识别效果）
    resized = cv2.resize(gray, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)

    return resized


def run_local_ocr_test(image_folder):
    """
    纯本地运行高准确率 OCR，识别指定文件夹下所有图片中的英文与日文
    """
    if not os.path.exists(image_folder):
        print(f"[错误] 找不到文件夹: {image_folder}")
        return

    # 找到所有的 PNG / JPG 截图
    image_paths = []
    for ext in ("*.png", "*.jpg", "*.jpeg"):
        image_paths.extend(glob.glob(os.path.join(image_folder, ext)))

    image_paths.sort()

    if not image_paths:
        print(f"[提示] 文件夹 '{image_folder}' 内未找到任何图片！")
        return

    output_txt = os.path.join(image_folder, "local_ocr_result.txt")

    print("=" * 60)
    print(f"找到 {len(image_paths)} 张图片。正在加载本地 EasyOCR (高精度配置)...")
    print("=" * 60)

    # 初始化本地 OCR 引擎
    reader = easyocr.Reader(['en', 'ja'], gpu=False)

    start_time = time.time()

    with open(output_txt, "w", encoding="utf-8") as f:
        for idx, img_path in enumerate(image_paths, start=1):
            file_name = os.path.basename(img_path)
            print(f"[{idx}/{len(image_paths)}] 正在处理并识别: {file_name} ...")

            try:
                # 图像预处理
                processed_img = preprocess_image(img_path)

                # 高准确率参数调优配置
                lines = reader.readtext(
                    processed_img,
                    detail=0,
                    paragraph=True,  # 合并属于同一段落的文本，增强行与句子的连贯性
                    contrast_ths=0.1,  # 对比度阈值（降低以增强浅色文字捕获）
                    adjust_contrast=0.5,  # 动态对比度调整
                    text_threshold=0.6  # 识别置信度阈值（防止漏识别小字或弱对比字）
                )

                f.write(f"==================== {file_name} ====================\n")
                for line in lines:
                    f.write(line + "\n")
                f.write("\n")

            except Exception as e:
                print(f"  [失败] 识别 {file_name} 时发生错误: {e}")

    elapsed = round(time.time() - start_time, 2)
    print("=" * 60)
    print(f"本地测试完成！耗时: {elapsed} 秒")
    print(f"识别结果已存入文件，请检查正确率：\n{output_txt}")
    print("=" * 60)


if __name__ == "__main__":
    target_dir = input("请输入需要测试识别的图片文件夹路径：").strip('"').strip()
    if target_dir:
        run_local_ocr_test(target_dir)
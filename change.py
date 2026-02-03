import os
import sys

# 【最高优先级】环境变量设置，必须在导入 AI 库之前
os.environ["FOR_DISABLE_CONSOLE_CTRL_HANDLER"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import torch

# 强制限制 Torch 线程，防止 Windows 底层数学库访问冲突
torch.set_num_threads(1)

import whisper
from tqdm import tqdm


def format_timestamp(seconds: float):
    m, s = divmod(int(seconds), 60)
    return f"[{m:02d}:{s:02d}]"


def transcribe_videos(input_dir, output_dir, model_type="small"):
    if not os.path.exists(input_dir):
        print(f"❌ 输入目录不存在: {input_dir}")
        return

    os.makedirs(output_dir, exist_ok=True)

    print(f"🚀 正在加载 Whisper 模型 ({model_type})...")
    try:
        # 显式指定使用 CPU 加载
        model = whisper.load_model(model_type, device="cpu")
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        return

    # 支持的媒体后缀
    video_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.flv', '.mp3', '.wav')
    all_files = [f for f in os.listdir(input_dir) if f.lower().endswith(video_extensions)]

    if not all_files:
        print("📭 文件夹中没有找到多媒体文件。")
        return

    print(f"✨ 找到 {len(all_files)} 个文件，准备开始转录...")

    for filename in tqdm(all_files, desc="总进度", unit="file"):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + ".txt")

        # 跳过已存在的文件
        if os.path.exists(output_path):
            continue

        try:
            # fp16=False 对 CPU 模式是强制要求的，verbose=False 提高运行稳定性
            result = model.transcribe(input_path, language="en", fp16=False, verbose=False)
            segments = result.get('segments', [])

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"--- {filename} 转录文本 ---\n\n")
                for i, seg in enumerate(segments):
                    time_mark = format_timestamp(seg['start'])
                    f.write(f"{time_mark} {seg['text'].strip()}\n")
                    if (i + 1) % 3 == 0:
                        f.write("\n")

        except Exception as e:
            print(f"\n⚠️ 处理 {filename} 时遇到问题: {e}")
            continue

    print("\n✅ 所有任务已完成！")


if __name__ == "__main__":
    # 路径确保正确 (原生字符串 r"...")
    my_input_dir = r"G:\TOEIC\TOEIC リスニング練習問題シリーズ"
    my_output_dir = r"G:\TOEIC\sub"

    # 第一次运行建议使用 base 模型验证环境稳定性
    transcribe_videos(my_input_dir, my_output_dir, model_type="base")
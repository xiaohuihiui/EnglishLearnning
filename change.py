import os

# 保持这些环境变量，它们能增加稳定性
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"

import whisper
from tqdm import tqdm

def format_timestamp(seconds: float):
    m, s = divmod(int(seconds), 60)
    return f"[{m:02d}:{s:02d}]"

def transcribe_videos(input_dir, output_dir, model_type="small"):
    if not os.path.exists(input_dir):
        print(f"错误：输入目录 {input_dir} 不存在")
        return

    print(f"正在加载原生 Whisper 模型 ({model_type})... 首次加载可能较慢...")

    try:
        # 原生 whisper 加载方式
        model = whisper.load_model(model_type, device="cpu")
    except Exception as e:
        print(f"模型加载失败: {e}")
        return

    os.makedirs(output_dir, exist_ok=True)

    video_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.flv', '.mp3', '.wav')
    all_files = [f for f in os.listdir(input_dir) if f.lower().endswith(video_extensions)]

    if not all_files:
        print("未找到支持的媒体文件。")
        return

    print(f"找到 {len(all_files)} 个文件，开始处理...")

    for filename in tqdm(all_files, desc="总进度", unit="file"):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + ".txt")

        if os.path.exists(output_path):
            continue

        try:
            # --- 注意：原生 whisper 的返回结构与 faster-whisper 不同 ---
            # 它直接返回一个包含 'segments' 键的字典
            result = model.transcribe(input_path, language="en", fp16=False)
            segments = result['segments']

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"--- {filename} 转录文本 ---\n\n")

                for i, seg in enumerate(segments):
                    # 原生 whisper 的 segment 是字典格式
                    start = format_timestamp(seg['start'])
                    text = seg['text'].strip()
                    f.write(f"{start} {text}\n")

                    if (i + 1) % 3 == 0:
                        f.write("\n")

        except Exception as e:
            print(f"\n处理文件 {filename} 时出错: {e}")
            continue

    print("\n✅ 所有任务处理完成！")

if __name__ == "__main__":
    my_input_dir = r"G:\TOEIC\word&phases"
    my_output_dir = r"G:\subtitle\word&phases"
    transcribe_videos(my_input_dir, my_output_dir, model_type="small")
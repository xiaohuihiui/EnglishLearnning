import os
import whisper
import ssl
import warnings
from tqdm import tqdm

# 1. 环境与警告设置
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")
ssl._create_default_https_context = ssl._create_unverified_context


def format_timestamp(seconds: float):
    """将秒数转换为 [mm:ss] 格式"""
    td = int(seconds)
    m, s = divmod(td, 60)
    return f"[{m:02d}:{s:02d}]"


def transcribe_videos(input_dir, output_dir, model_type="small"):
    print(f"正在加载 Whisper 模型 ({model_type})...")
    model = whisper.load_model(model_type)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    video_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.flv')
    all_files = [f for f in os.listdir(input_dir) if f.lower().endswith(video_extensions)]

    if not all_files:
        print("未找到视频文件。")
        return

    for filename in tqdm(all_files, desc="总进度", unit="file"):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.txt")

        if os.path.exists(output_path):
            continue

        # 执行转写
        # 使用 verbose=False 是为了我们自己控制输出格式
        result = model.transcribe(input_path, language="en", fp16=False)

        # --- 开始排版处理 ---
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"--- 视频文件: {filename} 转录文本 ---\n\n")

            # segments 包含了每一句的时间戳和文本
            for i, segment in enumerate(result["segments"]):
                start = format_timestamp(segment["start"])
                text = segment["text"].strip()

                # 每句开头带上时间戳，方便听力定位
                f.write(f"{start} {text}\n")

                # 每 3 句话多加一个换行符，形成段落，方便阅读
                if (i + 1) % 3 == 0:
                    f.write("\n")

        print(f"完成！已生成排版精美的文档: {output_path}")


if __name__ == "__main__":
    my_input_dir = "/Users/li/TOEIC"
    my_output_dir = "/Users/li/subTitle"
    transcribe_videos(my_input_dir, my_output_dir)
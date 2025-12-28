# import os
# from faster_whisper import WhisperModel
# from tqdm import tqdm
#
#
# def format_timestamp(seconds: float):
#     m, s = divmod(int(seconds), 60)
#     return f"[{m:02d}:{s:02d}]"
#
#
# def transcribe_videos(input_dir, output_dir, model_type="small"):
#     print(f"正在加载 Whisper 模型 ({model_type})...")
#     model = WhisperModel(
#         model_type,
#         device="cpu",
#         compute_type="int8",
#         cpu_threads=4
#     )
#
#     os.makedirs(output_dir, exist_ok=True)
#
#     video_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.flv')
#     all_files = [f for f in os.listdir(input_dir) if f.lower().endswith(video_extensions)]
#
#     if not all_files:
#         print("未找到视频文件。")
#         return
#
#     for filename in tqdm(all_files, desc="总进度", unit="file"):
#         input_path = os.path.join(input_dir, filename)
#         output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + ".txt")
#
#         if os.path.exists(output_path):
#             continue
#
#         segments, info = model.transcribe(input_path, language="en", beam_size=5)
#
#         with open(output_path, "w", encoding="utf-8") as f:
#             f.write(f"--- {filename} 转录文本 ---\n\n")
#
#             for i, seg in enumerate(segments):
#                 start = format_timestamp(seg.start)
#                 text = seg.text.strip()
#                 f.write(f"{start} {text}\n")
#
#                 if (i + 1) % 3 == 0:
#                     f.write("\n")
#
#         print(f"✔ 完成: {output_path}")
#
#
# if __name__ == "__main__":
#     my_input_dir = r"C:\GitCheck\English\videos"
#     my_output_dir = r"C:\GitCheck\English\subs"
#     transcribe_videos(my_input_dir, my_output_dir, model_type="small")

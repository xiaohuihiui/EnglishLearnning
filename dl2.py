import subprocess
from pathlib import Path
import sys


def main():
    print("=== yt-dlp 综合下载工具（PyCharm 版）===")
    print("支持：YouTube 视频、播放列表、音频提取\n")

    # 1. 输入 URL
    url = input("请输入 YouTube URL：\n> ").strip()
    if not url:
        print("❌ URL 不能为空")
        return

    # 2. 选择下载模式
    print("\n请选择下载模式：")
    print("[1] MP4 视频 (最高画质)")
    print("[2] MP3 音频 (最高音质)")
    choice = input("> ").strip()

    # 3. 设置保存目录
    base_dir_input = input("\n请输入保存目录（直接回车默认为当前文件夹下的 Downloads）：\n> ").strip()
    if not base_dir_input:
        base_dir = Path.cwd() / "Downloads"
    else:
        base_dir = Path(base_dir_input).resolve()

    base_dir.mkdir(parents=True, exist_ok=True)

    # 4. 配置输出模板
    # %(playlist_title)s 如果是单视频会显示为 None，yt-dlp 会自动处理
    output_template = str(
        base_dir / "%(playlist_title)s" / "%(playlist_index)s - %(title)s.%(ext)s"
        if "list" in url else
        base_dir / "%(title)s.%(ext)s"
    )

    # 5. 构建基础命令
    cmd = [
        "yt-dlp",
        "--cookies", "cookies.txt",  # 确保同目录下有此文件，或删除此行
        "--yes-playlist",
        "--sleep-interval", "2",
        "--max-sleep-interval", "5",
        "-o", output_template,
    ]

    # 6. 根据选择添加特定参数
    if choice == "2":
        # MP3 模式
        cmd.extend([
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "0",
        ])
        print("\n⚙️ 已选择：MP3 音频提取模式")
    else:
        # MP4 模式
        cmd.extend([
            "-f", "bv[ext=mp4][vcodec^=avc1]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b",
            "--merge-output-format", "mp4",
            "--recode-video", "mp4",
        ])
        print("\n⚙️ 已选择：MP4 视频下载模式")

    cmd.append(url)

    # 7. 执行命令
    print("\n>>> 开始下载...\n")
    try:
        # 使用 shell=False 在 Windows 上更安全
        subprocess.run(cmd, check=True)
        print(f"\n✅ 下载完成！文件保存在: {base_dir}")
    except subprocess.CalledProcessError:
        print("\n❌ 下载失败：请检查网络连接、FFmpeg 是否安装或 URL 是否正确。")
    except FileNotFoundError:
        print("\n❌ 错误：未找到 yt-dlp 或 FFmpeg，请确保它们已安装并添加到系统环境变量。")


if __name__ == "__main__":
    main()
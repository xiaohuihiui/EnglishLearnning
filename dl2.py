import os
import sys
import subprocess
from pathlib import Path


def setup_environment():
    """
    终极修复：动态获取当前 Python 解释器所在的路径，
    将其（以及对应的可执行文件目录）强行注入到环境变量 PATH 中，
    确保 subprocess 运行时能完美识别同环境下的 node.exe 和 ffmpeg.exe。
    """
    python_exe = Path(sys.executable)
    env_dir = python_exe.parent

    paths_to_add = [
        str(env_dir),  # Windows conda 环境的根目录或 Scripts 目录
        str(env_dir / "Scripts"),  # 存放 yt-dlp.exe, ffmpeg.exe 的地方
        str(env_dir / "Library" / "bin")  # 某些 conda 包装 node.exe 或 ffmpeg.exe 的地方
    ]

    current_path = os.environ.get("PATH", "")
    new_paths = [p for p in paths_to_add if p not in current_path]

    if new_paths:
        os.environ["PATH"] = os.path.pathsep.join(new_paths) + os.path.pathsep + current_path


def main():
    # 注入环境路径
    setup_environment()

    print("=== yt-dlp 综合下载工具（动态环境修复版） ===")
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
    default_dir = Path(r"D:\TOEIC\Youtube(practice)")
    base_dir_input = input(f"\n请输入保存目录（直接回车默认为 {default_dir}）：\n> ").strip()
    # base_dir_input = input("\n请输入保存目录（直接回车默认为当前文件夹下的 Downloads）：\n> ").strip()
    if not base_dir_input:
        # base_dir = Path.cwd() / "Downloads"
        base_dir = default_dir
    else:
        base_dir = Path(base_dir_input).resolve()
    base_dir.mkdir(parents=True, exist_ok=True)

    # 4. 智能输出模板：区分单视频和播放列表
    if "list" in url:
        output_template = str(
            base_dir / "%(playlist_title)s" / "%(playlist_index)s - %(title)s.%(ext)s"
        )
    else:
        output_template = str(base_dir / "%(title)s.%(ext)s")

    # 5. 构建核心命令（纯免 Cookie & 免 Token 全自动配置）
    cmd = [
        "yt-dlp",
        # 使用完全不需要 PO Token 和 Cookie 的客户端组合，适合批量下载
        "--extractor-args", "youtube:player-client=android_vr,ios",
        "--yes-playlist",
        "--sleep-interval", "3",
        "--max-sleep-interval", "7",
        "--ignore-errors",
        "-o", output_template,
    ]

    # 6. 根据选择添加特定参数
    if choice == "2":
        # MP3 模式
        cmd.extend([
            "-x",
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
        # 使用 shell=False
        subprocess.run(cmd, check=True)
        print(f"\n✅ 下载流程结束！查看目录: {base_dir}")
    except subprocess.CalledProcessError:
        print("\n❌ 下载中断或遇到严重错误。")
    except FileNotFoundError:
        print("\n❌ 错误：未找到 yt-dlp 或 FFmpeg，请确保它们已安装。")


if __name__ == "__main__":
    main()
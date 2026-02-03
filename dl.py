import subprocess
from pathlib import Path


def main():
    print("=== yt-dlp 播放列表下载工具（PyCharm 版）===\n")

    url = input("请输入 YouTube 视频 / 播放列表 URL：\n> ").strip()
    if not url:
        print("❌ URL 不能为空")
        return

    base_dir_input = input("\n请输入保存目录（如 G:\\EnglishLearnning\\Downloads）：\n> ").strip()
    if not base_dir_input:
        print("❌ 保存目录不能为空")
        return

    base_dir = Path(base_dir_input).resolve()
    base_dir.mkdir(parents=True, exist_ok=True)

    output_template = str(
        base_dir
        / "%(playlist_title)s"
        / "%(playlist_index)02d - %(title)s.%(ext)s"
    )

    archive_file = base_dir / "archive.txt"

    cmd = [
        "yt-dlp",
        "--cookies", "cookies.txt",
        "--js-runtimes", "node",
        "--remote-components", "ejs:github",
        "--yes-playlist",
       # "--download-archive", str(archive_file),
        "--sleep-interval", "2",
        "--max-sleep-interval", "5",
        "-f", "bv*+ba/b",
        "--merge-output-format", "mp4",
        "-o", output_template,
        url,
    ]

    print("\n>>> 即将执行 yt-dlp 命令：\n")
    print(" ".join(cmd))
    print("\n>>> 开始下载...\n")

    try:
        subprocess.run(cmd, check=True)
        print("\n✅ 下载完成")
    except subprocess.CalledProcessError:
        print("\n❌ 下载失败，请检查上面的错误信息")


if __name__ == "__main__":
    main()

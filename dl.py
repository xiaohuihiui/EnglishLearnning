import yt_dlp
import os


def download_youtube_playlist(playlist_url, save_path='downloads'):
    # 如果目录不存在则创建
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # 下载配置
    ydl_opts = {
        # 格式选择：最佳视频 + 最佳音频 / 最佳混合
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',

        # 保存路径和文件名模板 (序号 - 标题.扩展名)
        'outtmpl': f'{save_path}/%(playlist_index)s - %(title)s.%(ext)s',

        # 额外参数
        'ignoreerrors': True,  # 遇到单个视频错误时跳过，继续下载后续视频
        'quiet': False,  # 显示下载进度
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"正在获取播放列表信息: {playlist_url}")
            ydl.download([playlist_url])
        print("\n所有任务处理完毕！")
    except Exception as e:
        print(f"发生错误: {e}")


if __name__ == "__main__":
    url = input("请输入 YouTube 播放列表 URL: ").strip()
    path = input("请输入保存文件夹名称 (直接回车默认 'downloads'): ").strip()

    download_youtube_playlist(url, path if path else 'downloads')
import os

print("=== YouTube 播放列表一键下载器 ===")

playlist_url = input("请输入播放列表链接: ").strip()
save_path = input("请输入保存路径 (如 D:/YouTube): ").strip()

if not playlist_url.startswith("http"):
    print("❌ 播放列表链接格式错误")
    exit()

if not os.path.exists(save_path):
    os.makedirs(save_path)

cmd = (
    f'yt-dlp '
    f'--cookies cookies.txt '
    f'-P "{save_path}" '
    f'-o "%(playlist_index)02d - %(title)s.%(ext)s" '
    f'-f "bv*[height<=1080]+ba/b" '
    f'-N 8 --sleep-interval 2 --max-sleep-interval 5 '
    f'"{playlist_url}"'
)

print("\n开始下载...\n")
os.system(cmd)

print("\n🎉 下载完成！")

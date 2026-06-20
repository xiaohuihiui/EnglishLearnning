from googletrans import Translator
import re

# 输入和输出文件
input_srt = "video.srt"
output_srt = "video_ja.srt"

translator = Translator()

def translate_line(line):
    # 翻译字幕行
    return translator.translate(line, src='en', dest='ja').text

with open(input_srt, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # 如果是字幕文本行（不是时间轴或编号）
    if re.match(r'^\d+$', line) or re.match(r'\d{2}:\d{2}:\d{2},\d{3}', line) or line.strip() == '':
        new_lines.append(line)
    else:
        translated = translate_line(line.strip())
        new_lines.append(translated + '\n')

with open(output_srt, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"日文字幕已生成：{output_srt}")
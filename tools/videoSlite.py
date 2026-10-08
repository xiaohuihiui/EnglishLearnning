from pydub import AudioSegment
from pydub.silence import split_on_silence

# 读取上传的长语音文件
sound = AudioSegment.from_mp3("WL0184_03634-03641.mp3")

# 根据静音切分（当静音时间大于500毫秒，且声音小于-40dBFS时切断）
chunks = split_on_silence(sound, min_silence_len=500, silence_thresh=-40)

# 循环保存为小语音文件
for i, chunk in enumerate(chunks):
    chunk.export(f"./audio/word_{i}.mp3", format="mp3")

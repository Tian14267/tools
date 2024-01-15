import os
from tqdm import tqdm
import soundfile
from pypinyin import pinyin, Style

def write_file(lines,file):
	with open(file,"w",encoding="utf-8") as f:
		for line in lines:
			line = line + "\n"
			f.write(line)
	f.close()


def is_chinese(str_input):
	"""判断一个unicode是否是汉字"""
	for char in str_input:
		if '\u4e00' <= char <= '\u9fff':
			return True

	return False


####  检测语音名字中是否有汉字，并转成拼音
###  未完工  --  不可用
def rename_wav(wav_input):
	wav_name = wav_input.split("/")[-1]
	wav_name = wav_name.replace("-","")
	wav_name_split = wav_name.split("_")
	new_wav_list = []
	for one_name in wav_name_split:
		if is_chinese(one_name):
			pinyins = [
				p[0]
				for p in pinyin(
					one_name, style=Style.TONE3, strict=False, neutral_tone_with_five=True
				)
			]
			one_name_pinyin = "".join(pinyins)
			new_wav_list.append(one_name_pinyin)
		else:
			new_wav_list.append(one_name)

	new_wav_name = "_".join(new_wav_list)
	return new_wav_name



def main():
	audio_dir = "/sdb/fffan/0_data/9_tools/6_covert_to_wav/mp3_to_wav"
	all_wav_path = []
	for subfolder, _, filelist in tqdm(sorted(os.walk(audio_dir))):
		for fname in filelist:
			if ".wav" in fname:
				audio_path = os.path.abspath(os.path.join(subfolder, fname))
				all_wav_path.append(audio_path)
	#all_wav_path = ["/sdb/fffan/0_data/9_tools/6_covert_to_wav/mp3_to_wav/张玉凤_15974070276_147_20200507165829_out.wav"]
	error_list = []
	select_wav_list = []
	for one_wav in tqdm(all_wav_path):
		try:
			audio_data, samplerate = soundfile.read(one_wav)
			duration = float(len(audio_data) / samplerate)
			##########
			if duration < 10: ####  筛选出小于10s的语音
				continue
			select_wav_list.append(one_wav)
		except:
			error_list.append(one_wav)


	#####  转移筛选数据
	out_path = "./data_out/0_select_data_dingzhong_RR_"
	os.makedirs(out_path, exist_ok=True)
	for one_wav in tqdm(select_wav_list):
		out_name = os.path.join(out_path,rename_wav(one_wav))  ###  重命名
		line  = "cp " + one_wav + " "+out_name
		os.system(line)

	if error_list:
		write_file(error_list,"./0_error_list.txt")


if __name__ == '__main__':
	'''
	主函数入口
	'''
	# 调用文件夹读取批量文件
	main()


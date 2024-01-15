import os
import pickle
import json
import argparse
from tqdm import tqdm
import numpy as np
import librosa
import wave
import argparse
import soundfile as sf
from scipy.io import wavfile
from multiprocessing import Manager, Process

def read_files(file):
	with open(file,"r",encoding="utf-8") as f:
	#with open(file, "r", encoding="GBK") as f:
		lines = f.readlines()
		lines_out = []
		for line in lines:
			line = line.replace("\n","")
			lines_out.append(line)
	f.close()
	return lines_out

def write_file(lines,file):
	with open(file,"w",encoding="utf-8") as f:
		for line in lines:
			line = str(line) + "\n"
			f.write(line)
	f.close()

def read_wave_from_file(audio_file):
	"""
	return 一维numpy数组，如（584,） 采样率"""
	wav = wave.open(audio_file, 'rb')
	num_frames = wav.getnframes()
	framerate = wav.getframerate()
	str_data = wav.readframes(num_frames)
	wav.close()
	wave_data = np.frombuffer(str_data, dtype=np.short)
	return wave_data, framerate

#################################################################################################################

def re_sample_wav(process_id, input_list, start, end ,sample_rate, original_path, out_path):
	one_list = input_list[start:end]
	print("###  进程 ", str(process_id), "数据量：", len(one_list))
	print(start, end)

	for one_line in tqdm(one_list, desc="进程" + str(process_id) + ": "):
		####
		#wav_name = one_line.split("/")[-1]
		#one_input_path = one_line.replace(wav_name, "")
		one_out_wav_path = one_line.replace(original_path, out_path)

		############################################################
		audio, sampling_rate = read_wave_from_file(one_line)
		max_value = float(max(audio))
		#####
		wav, _ = librosa.load(path=one_line, sr=sample_rate)
		resample_wav = wav / max(abs(wav)) * max_value
		# """
		wavfile.write(
			one_out_wav_path,
			sample_rate,
			resample_wav.astype(np.int16),
		)
		#"""
	#################################################################

def mutil_process(input_lines, process_num,  reample_rate,original_path, out_path):
	from multiprocessing import Manager, Process
	print("###  数据总量：", len(input_lines))

	each_len = len(input_lines) / process_num
	p_list = []
	for i in range(process_num):
		if i == process_num - 1:
			p = Process(target=re_sample_wav,
			            args=(i, input_lines, int(each_len * i), len(input_lines), reample_rate, original_path, out_path))
		else:
			p = Process(target=re_sample_wav,
			            args=(i, input_lines, int(each_len * i), int(each_len * (i + 1)), reample_rate, original_path, out_path))
		p.start()
		p_list.append(p)
	for res in p_list:
		res.join()

	print("### 多进程处理数据完成。")


##############################################
def main():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--data_path",
	                    default="/data/fffan/3_data/TTS/AISHELL-3",
	                    type=str, help=" ")
	parser.add_argument("--re_sample_rate",
	                    default=8000, help="")
	parser.add_argument("--process_num",
	                    default=16, help="")
	parser.add_argument("--output_path",
	                    default="./aishell3_8k",
	                    type=str, help=" ")
	parser.add_argument("--label_path",
	                    default="",
	                    type=str, help=" ")
	args = parser.parse_args()

	########################################################
	###      读取语音目录
	all_file_list = []
	for path, dir_list, file_list in os.walk(args.data_path):
		for file_name in file_list:
			if ".wav" in file_name:
				all_file_list.append(os.path.join(path, file_name))
	########################################################

	assert args.data_path[-1] != "/","最后一个字符不能是 /"
	assert args.output_path[-1] != "/","最后一个字符不能是 /"

	#######       创建目录
	all_wav_out_path = []
	for one_line in all_file_list:
		wav_name = one_line.split("/")[-1]
		one_path = one_line.replace(wav_name,"")

		one_path_out = one_path.replace(args.data_path,args.output_path)
		all_wav_out_path.append(one_path_out)

	all_wav_out_path = list(set(all_wav_out_path))
	for one_path in all_wav_out_path:
		#print(one_path)
		os.makedirs(one_path, exist_ok=True)
	#exit()

	##################################################
	##################################################
	mutil_process(all_file_list, args.process_num, args.re_sample_rate, args.data_path, args.output_path)




if __name__ == "__main__":
	main()
	
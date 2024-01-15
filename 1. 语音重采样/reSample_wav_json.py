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

def re_sample_wav(process_id, input_list, start, end ,sample_rate, out_path):
	one_list = input_list[start:end]
	print("###  进程 ", str(process_id), "数据量：", len(one_list))
	print(start, end)

	resample_name = "_"+str(int(sample_rate/1000))+"k"
	for one_line in tqdm(one_list, desc="进程" + str(process_id) + ": "):
		####
		wav_name = one_line.split("/")[-1]
		new_wav_name = wav_name.replace("_8k",resample_name)
		#file_name = one_line.split("/")[-2]
		file_name = ""
		############################################################

		audio, sampling_rate = read_wave_from_file(one_line)
		max_value = float(max(audio))
		#####
		wav, _ = librosa.load(path=one_line, sr=sample_rate)
		resample_wav = wav / max(abs(wav)) * max_value
		# """
		wavfile.write(
			os.path.join(out_path, file_name, new_wav_name),
			sample_rate,
			resample_wav.astype(np.int16),
		)
		#"""
	#################################################################

def mutil_process(input_lines, process_num,  reample_rate, out_path):
	from multiprocessing import Manager, Process
	print("###  数据总量：", len(input_lines))

	each_len = len(input_lines) / process_num
	p_list = []
	for i in range(process_num):
		if i == process_num - 1:
			p = Process(target=re_sample_wav,
			            args=(i, input_lines, int(each_len * i), len(input_lines), reample_rate,  out_path))
		else:
			p = Process(target=re_sample_wav,
			            args=(i, input_lines, int(each_len * i), int(each_len * (i + 1)), reample_rate,  out_path))
		p.start()
		p_list.append(p)
	for res in p_list:
		res.join()

	print("### 多进程处理数据完成。")

##############################################
def deal_wav_label_data(label_path):
	lines = read_files(label_path)
	new_lines = []
	for one_line in lines:
		one_line = one_line.replace("_8k","_16k")
		new_lines.append(one_line)
	write_file(new_lines, "./online_cut_data_labels.txt")

##############################################
def main():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--data_path",
	                    default="/ultra/fffan/1_data/asr_original_data/0_线上_data/9_tools/3_数据筛选/temp_shuf_cut.txt",
	                    type=str, help=" ")
	parser.add_argument("--re_sample_rate",
	                    default=16000, help="")
	parser.add_argument("--process_num",
	                    default=30, help="")
	parser.add_argument("--output_path",
	                    default="./wav_16k",
	                    type=str, help=" ")
	parser.add_argument("--label_path",
	                    default="/ultra/fffan/1_data/asr_original_data/0_线上_data/3_语音切分/1_训练数据/1_human_voice/human_label_list.txt",
	                    type=str, help=" ")
	args = parser.parse_args()

	lines = read_files(args.data_path)
	##################################################
	file_name_list = []
	wav_text_list = []
	for one_line in lines:
		one_line = one_line.replace("\'","\"")
		one_json = json.loads(one_line)
		if "path" in one_json.keys() and "text" in one_json.keys():
			one_data_path = one_json["path"]
			one_text = one_json["text"].replace(" ","")
			file_name_list.append(one_data_path)
			wav_name = one_data_path.split("/")[-1]
			wav_text_list.append(wav_name+" "+one_text)
	file_name_list = list(set(file_name_list))
	#file_name_list = file_name_list[:100]
	os.makedirs(args.output_path, exist_ok=True)
	##################################################
	#re_sample_wav(0, lines, 0,1000, args.re_sample_rate, args.output_path)
	mutil_process(file_name_list, args.process_num, args.re_sample_rate, args.output_path)
	#deal_wav_label_data(args.label_path)
	write_file(wav_text_list, "./cut_data_labels.txt")



if __name__ == "__main__":
	main()
	
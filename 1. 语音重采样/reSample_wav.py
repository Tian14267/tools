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
		new_wav_name = wav_name.replace("_16k",resample_name).replace("-","_")
		file_name = one_line.split("/")[-2]

		out_file_path = os.path.join(out_path, file_name)
		os.makedirs(out_file_path, exist_ok=True)
		############################################################
		try:
			audio, sampling_rate = read_wave_from_file(one_line)
			max_value = float(max(audio))
			#####
			wav, _ = librosa.load(path=one_line, sr=sample_rate)
			resample_wav = wav / max(abs(wav)) * max_value
			# """
			wavfile.write(
				os.path.join(out_file_path, new_wav_name),
				sample_rate,
				resample_wav.astype(np.int16),
			)
		# """

		except:
			print(one_line)
			print(new_wav_name)
			print("#############################################")




def re_sample_wav_sox(process_id, input_list, start, end ,sample_rate, out_path):
	one_list = input_list[start:end]
	print("###  进程 ", str(process_id), "数据量：", len(one_list))
	print(start, end)

	resample_name = "_"+str(int(sample_rate/1000))+"k"
	resample_list = []
	for one_line in one_list:
		####
		wav_name = one_line.split("/")[-1]
		new_wav_name = wav_name.replace("_8k",resample_name).replace("-","_")
		file_name = one_line.split("/")[-2]
		############################################################
		#####
		line = "sox " + one_line + " -r " + str(sample_rate)+" " + os.path.join(out_path, file_name, new_wav_name)
		resample_list.append(line)
	one_list = []

	#print(resample_list[0])
	for resample_line in tqdm(resample_list, desc="进程" + str(process_id) + ": "):
		os.system(resample_line)
	#################################################################
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
def deal_wav_label_data(label_path, new_wav_path):
	lines = read_files(label_path)
	new_lines = {}
	for one_line in lines:
		wav_ = one_line.split(" ",1)[0].replace(".wav","")
		one_line = one_line.replace("_16k","_8k").replace("-","_")
		new_lines[wav_] = one_line

	all_wav_file_list = {}
	for path, dir_list, file_list in os.walk(new_wav_path):
		for file_name in file_list:
			if ".wav" in file_name:
				wav_name = file_name.replace(".wav","")
				all_wav_file_list[wav_name] =os.path.join(path, file_name)
				#all_wav_file_list.append(os.path.join(path, file_name))

	wav_list = set(new_lines).intersection(set(all_wav_file_list))

	out_list = []
	for one in list(wav_list):
		out_list.append(new_lines[one])

	write_file(out_list, "./text_aishell.txt")

##############################################
def main():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--data_path",
	                    default="/sdb/fffan/0_data/1_resample_data/16k_wav/aishell/wav_aishell.txt",
	                    type=str, help=" ")
	parser.add_argument("--re_sample_rate",
	                    default=8000, help="")
	parser.add_argument("--process_num",
	                    default=30, help="")
	parser.add_argument("--output_path",
	                    default="/sdb/fffan/0_data/1_resample_data/8k_wav/aishell_8k/wav",
	                    type=str, help=" ")
	parser.add_argument("--label_path",
	                    default="/sdb/fffan/0_data/1_resample_data/16k_wav/aishell/aishell_text.txt",
	                    type=str, help=" ")
	args = parser.parse_args()

	lines = read_files(args.data_path)
	##################################################
	file_name_list = []
	for one_line in lines:
		file_name_list.append(one_line.split("/")[-2])
	file_name_list = list(set(file_name_list))
	for one_file in file_name_list:
		os.makedirs(os.path.join(args.output_path, one_file), exist_ok=True)
	##################################################

	mutil_process(lines, args.process_num, args.re_sample_rate, args.output_path)
	deal_wav_label_data(args.label_path, args.output_path)



if __name__ == "__main__":
	main()
	
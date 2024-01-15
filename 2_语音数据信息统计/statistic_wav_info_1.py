import os
import pickle
import json
import wave
import numpy as np
from tqdm import tqdm

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

#######################################################################################################################
def statistic_function(process_id, wav_list, wav_info_dict, start,  end):
	one_list = wav_list[start:end]
	print("###  进程 ",str(process_id),"数据量：",len(one_list))
	print(start,end)
	file_info_list = []
	for one_wav in tqdm(one_list,desc="进程"+str(process_id)+": "):
		wav_path, wav_text = wav_info_dict[one_wav]
		#audio, sampling_rate = read_wave_from_file(wav_path)
		#wav_time = float(len(audio)/sampling_rate)
		with wave.open(wav_path, 'rb') as f:
			wav_time = f.getparams().nframes / f.getparams().framerate
			info_temp = {"id":one_wav,"path":wav_path,"wav_len": wav_time,"text": wav_text}
			file_info_list.append(info_temp)
		#info_temp = {"id": one_wav, "path": wav_path, "wav_len": wav_time, "text": wav_text}
		#file_info_list.append(info_temp)
	file_name = "./wav_info_0/"+str(process_id)+"_"+str(start)+"_"+str(end)+"_wav_info.txt"
	write_file(file_info_list,file_name)


def mutil_process(input_dict):
	from multiprocessing import Manager, Process
	input_lines = list(input_dict.keys())
	print("###  数据总量：", len(input_lines))
	thread = 35
	each_len = len(input_lines) / thread
	p_list = []
	for i in range(thread):
		if i == thread - 1:
			p = Process(target=statistic_function, args=(i, input_lines,input_dict, int(each_len * i), len(input_lines)))
		else:
			p = Process(target=statistic_function, args=(i, input_lines,input_dict, int(each_len * i), int(each_len * (i + 1))))
		p.start()
		p_list.append(p)
	for res in p_list:
		res.join()

	print("### 多进程处理数据完成。")

def statistic_wav_info_all():
	####  读取所有语音路径
	print("####  读取所有语音路径")
	wav_list = read_files("/data/data_filter/wav.scp")
	wav_name_path_dict = {}
	for one_line in tqdm(wav_list,desc='wav_name_path: '):
		wav_name,wav_path = one_line.split(" ")
		wav_name_path_dict[wav_name] = wav_path

	print("####  读取所有语音文本信息")
	####  读取所有语音文本信息
	wav_text_list = read_files("./split_00")
	wav_name_text_dict = {}
	wav_info_dict = {}

	for one_line in tqdm(wav_text_list,desc='wav_name_text: '):
		wav_name, wav_text = one_line.split("	")
		wav_info_dict[wav_name] = [wav_name_path_dict[wav_name],wav_text]

	#statistic_function(0,list(wav_info_dict.keys()),wav_info_dict,0,100 )
	mutil_process(wav_info_dict)

#######################################################################################################################################################

def statistic_info():
	import json
	###  读取语音数据
	wav_list = read_files("/ultra/fffan/1_data/asr_original_data/0_线上_data/3_语音切分/1_训练数据/1_human_voice_list.txt")
	wav_path_dict = {}
	for one_wav in wav_list:
		wav_name = one_wav.split("/")[-1]
		wav_path_dict[wav_name] = one_wav
	print(wav_name)

	####  读取语音信息（16k） -- 获取语音时长
	wav_info_list = read_files("/ultra/fffan/1_data/asr_original_data/0_线上_data/9_tools/2_语音重采样/wav_info.txt")
	wav_16k_len_dict = {}
	for one_wav in wav_info_list:
		one_wav_json = json.loads(one_wav)
		wav_name = one_wav_json['utt'].replace("_16k","_8k")+".wav"
		wav_len =  one_wav_json['feat_shape'][0]
		wav_text = one_wav_json['text']
		wav_16k_len_dict[wav_name] = {"wav_len":wav_len, "text":wav_text}
	print(wav_name)

	#####
	all_wav_info = {}
	all_wav_info_list = []
	error_list = []
	for one_wav in tqdm(wav_16k_len_dict.keys()):
		if one_wav in wav_path_dict.keys():
			all_wav_info_list.append({
				"id":one_wav,
				"path":wav_path_dict[one_wav],
				"wav_len": wav_16k_len_dict[one_wav]["wav_len"],
				"text": wav_16k_len_dict[one_wav]["text"]
			})
		else:
			error_list.append(one_wav)
	print(error_list)

	write_file(all_wav_info_list,"online_wav_info_.txt")


def select_wav():
	####  筛选出符合条件的语音数据
	#with open("./online_wav_info.json", 'r', encoding='utf8') as fp:
	#	json_data = json.load(fp)
	lines = read_files("/ultra/fffan/1_data/asr_original_data/0_线上_data/3_语音切分/1_训练数据/1_human_voice/online_wav_info.txt")
	wav_select = []
	wav_path_list = []
	wav_text_list = []
	for one_line in tqdm(lines):
		#one_line = one_line.replace("\'","\"")
		#one_line_json = json.loads(one_line)
		one_line_json = eval(one_line)
		wav_name = one_line_json["id"].replace(".wav","")
		wav_len = float(one_line_json["wav_len"])

		#one_line_json["path"].replace("/ultra/fffan/1_data/asr_original_data/0_线上_data/9_tools/2_语音重采样/wav_16k","/data/TrainSegWav/8k/CrudeTrans/onlinedata_20220923/wav")
		wav_path = os.path.join("/data/TrainSegWav/8k/CrudeTrans/onlinedata_20220923/wav",wav_name+".wav")
		if wav_len>1.0:
			wav_select.append(one_line)
			wav_path_list.append(wav_name+" "+wav_path)
			wav_text_list.append(wav_name + "\t" + one_line_json["text"])

	#write_file(wav_select, "online_wav_time_1s+_.txt")
	write_file(wav_path_list, "online_wav_path_1s+.txt")
	write_file(wav_text_list, "online_wav_text_1s+.txt")



if __name__ == "__main__":
	#statistic_info()
	select_wav()
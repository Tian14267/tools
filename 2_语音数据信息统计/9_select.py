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


#######################################################################################################################################################
def run_function(process_id, input_list, start, end, l):
	one_list = input_list[start:end]
	print("###  进程 ", str(process_id), "数据量：", len(one_list))
	print(start, end)
	wav_dict = {}
	for one_line in tqdm(one_list, desc="进程" + str(process_id) + ": "):
		one_wav_json = json.loads(one_line)
		wav_path = one_wav_json["audio_path"]
		wav_text = one_wav_json["text"]
		wav_id = one_wav_json["utt"]
		wav_dur = one_wav_json["audio_duration"]

		wav_file_name = wav_path.split("/")[-3]
		assert "wav" in wav_file_name
		utt2spk = wav_path.split("/")[-2]
		new_json = {}
		new_json["utt"] = wav_id
		new_json["utt2spk"] = utt2spk
		new_json["feat"] = wav_path
		new_json["feat_shape"] = wav_dur
		new_json["text"] = wav_text

		if wav_file_name not in wav_dict.keys():
			wav_dict[wav_file_name] = [new_json]
		else:
			wav_dict[wav_file_name] = wav_dict[wav_file_name] + [new_json]

	l.append([wav_dict])


def mutil_process(input_lines):
	from multiprocessing import Manager, Process
	print("###  数据总量：", len(input_lines))
	if len(input_lines) == 0:
		print("#####   数据有问题！")
		exit()
	# 生成Manager对象
	manager = Manager()
	l = manager.list()
	thread = 35
	each_len = len(input_lines) / thread
	p_list = []
	for i in range(thread):
		if i == thread - 1:
			p = Process(target=run_function,
						args=(i, input_lines, int(each_len * i), len(input_lines), l ))
		else:
			p = Process(target=run_function,
						args=(i, input_lines, int(each_len * i), int(each_len * (i + 1)), l ))
		p.start()
		p_list.append(p)
	for res in p_list:
		res.join()

	wav_all_dict = {}
	for one_dict_list in l:
		for one_dict in one_dict_list:
			for one_key in one_dict.keys():
				if one_key not in wav_all_dict.keys():
					wav_all_dict[one_key] = one_dict[one_key]
				else:
					wav_all_dict[one_key] = wav_all_dict[one_key] + one_dict[one_key]

	return wav_all_dict


def main():
	lines = read_files("./data_wespeech/data_out/manifest.all")
	#lines = lines[:100000]
	wav_dict = mutil_process(lines)

	for one_wav_file in wav_dict.keys():
		name = "./data/"+one_wav_file+".txt"
		write_file(wav_dict[one_wav_file],name)


if __name__ == "__main__":
	main()
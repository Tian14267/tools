#coding: utf-8
import argparse
import codecs
import json
import os
import random
from pathlib import Path
from tqdm import tqdm
import soundfile
from concurrent.futures import ThreadPoolExecutor
import threading
from multiprocessing.dummy import Pool


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
			line = line + "\n"
			f.write(line)
	f.close()

###########
########################################################################################################################
###  多进程
def run_function(process_id, input_list, start, end, l):
	one_list = input_list[start:end]
	print("###  进程 ", str(process_id), "数据量：", len(one_list))
	print(start, end)
	process_duration_list = []
	for line in tqdm(one_list):
		line = line.replace("audio_apth", "audio_path")
		one_wav_json = json.loads(line)
		# wav_path = one_wav_json["audio_path"]
		duration = float(one_wav_json["audio_duration"][0])
		process_duration_list.append(duration)

	l.append(process_duration_list)


def run_ppasr_function(process_id, input_list, start, end, l):
	one_list = input_list[start:end]
	print("###  进程 ", str(process_id), "数据量：", len(one_list))
	print(start, end)
	process_duration_list = []
	for line in tqdm(one_list):
		one_wav_json = json.loads(line)
		# wav_path = one_wav_json["audio_path"]
		duration = float(one_wav_json["duration"])
		process_duration_list.append(duration)

	l.append(process_duration_list)

def mutil_process_function(input_lines):
	from multiprocessing import Manager, Process
	print("###  数据总量：", len(input_lines))
	if len(input_lines) == 0:
		print("#####   数据有问题！")
		exit()
	# 生成Manager对象
	manager = Manager()
	l = manager.list()
	thread = 30
	each_len = len(input_lines) / thread
	p_list = []
	for i in range(thread):
		if i == thread - 1:
			p = Process(target=run_ppasr_function,
						args=(i, input_lines, int(each_len * i), len(input_lines), l ))
		else:
			p = Process(target=run_ppasr_function,
						args=(i, input_lines, int(each_len * i), int(each_len * (i + 1)), l ))
		p.start()
		p_list.append(p)
	for res in p_list:
		res.join()

	total_sec = 0.0
	total_num = 0
	for one_l in l:
		one_l_num = len(one_l)
		one_l_sec = sum(one_l)
		total_sec = total_sec + one_l_sec
		total_num = total_num + one_l_num

	return total_sec, total_num


####  多进程处理
def statistic_wav_info(data_dir,out_path, file_name):
	print("Saitisitc manifest ..." )
	all_wav_info = read_files(data_dir)

	mutil_process = True  ####  是否多进程

	if mutil_process:
		##############################
		###  多进程
		total_sec, total_num = mutil_process_function(all_wav_info)
	else:
		######  单进程
		duration_list = []
		for line in tqdm(all_wav_info):
			line = line.replace("audio_apth", "audio_path")
			one_wav_json = json.loads(line)
			#wav_path = one_wav_json["audio_path"]
			duration = float(one_wav_json["audio_duration"][0])
			duration_list.append(duration)

		total_sec = sum(duration_list)
		total_num = len(duration_list)


	# manifest_dir = os.path.dirname(manifest_path_prefix)
	meta_path = os.path.join(out_path, file_name+"_info.txt")
	with open(meta_path, 'w') as f:
		print(f"{file_name}:", file=f)
		print(f"{total_num} utts", file=f)
		print(f"{total_sec / (60 * 60)} h", file=f)
		#print(f"{total_text} text", file=f)
		#print(f"{total_text / total_sec} text/sec", file=f)
		#print(f"{total_sec / total_num} sec/utt", file=f)



def main():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--data",default="/sdb/fffan/1_paddle/PPASR_develop_u2_1114/dataset/manifest_no_wespeech_test.raw",
	                    type=str, help="manifest")
	parser.add_argument("--out_path",default="./",type=str, help="")
	parser.add_argument("--out_file_name", default="temp_test", type=str, help="")
	args = parser.parse_args()

	os.makedirs(args.out_path, exist_ok=True)
	#####  多进程处理数据
	statistic_wav_info(args.data,  args.out_path, args.out_file_name)



if __name__ == '__main__':
	main()

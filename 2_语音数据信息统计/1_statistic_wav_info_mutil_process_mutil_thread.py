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
##  多线程
def run_func_thread(process_input ):
	process_id, thread_id, input_list, start, end, transcript_dict = process_input
	one_list = input_list[start:end]
	print("###  线程 ", str(thread_id), "数据量：", len(one_list))
	print(start, end)
	total_sec = 0.0
	total_text = 0.0
	total_num = 0
	json_lines = []
	for one_audio_path in tqdm(one_list, desc="进程" + str(process_id) +" 线程"+str(thread_id)+ ": "):
		audio_path = one_audio_path
		audio_id = one_audio_path.split("/")[-1].replace(".wav", "")
		# if no transcription for audio then skipped
		if audio_id not in transcript_dict:
			continue

		try:
			audio_data, samplerate = soundfile.read(audio_path)
		except:
			continue

		duration = float(len(audio_data) / samplerate)
		text = transcript_dict[audio_id]
		json_lines.append(
			json.dumps(
				{
					'utt': audio_id,
					# 'utt2spk': str(utt2spk),
					'audio_path': audio_path,
					'audio_duration': (duration,),  # second
					'text': text
				},
				ensure_ascii=False))
		total_sec += duration
		total_text += len(text)
		total_num += 1
	print("###  进程 ",process_id," 线程 ",thread_id,"：",len(json_lines))
	thread_out = [json_lines, total_sec, total_text, total_num]
	return thread_out

def mutil_thread(process_id, input_lines,transcript_dict):
	#input_lines = input_lines[:100]
	print("###  数据总量：", len(input_lines))
	if len(input_lines) == 0:
		print("#####   数据有问题！")
		exit()
	thread_num = 10

	each_len = len(input_lines) / thread_num

	#with ThreadPoolExecutor(max_workers=thread_num) as pool:
	with ThreadPoolExecutor(max_workers=thread_num+1) as pool:
		pool_parameter = []
		for i in range(thread_num):
			if i == thread_num - 1:
				pool_parameter.append([process_id, i, input_lines,int(each_len * i), len(input_lines),transcript_dict])
			else:
				pool_parameter.append([process_id, i, input_lines, int(each_len * i), int(each_len * (i + 1)), transcript_dict])

		results = pool.map(run_func_thread, pool_parameter)

	json_lines = []
	total_sec = 0.0
	total_text = 0.0
	total_num = 0
	for one_l in results:
		json_lines = json_lines + one_l[0]
		total_sec = total_sec + one_l[1]
		total_text = total_text + one_l[2]
		total_num = total_num + one_l[3]
	all_result = [json_lines,total_sec, total_text,total_num]
	#print("#####  ", json_lines)
	#print("#####  ", len(json_lines))
	#print("#####  json_lines_all: ", json_lines[3])
	#print("#####  total_text_all: ", total_text)
	return all_result
########################################################################################################################
###  多进程
def run_function(process_id, input_list, start, end, l, transcript_dict):
	one_list = input_list[start:end]
	print("###  进程 ", str(process_id), "数据量：", len(one_list))
	print(start, end)
	process_out = mutil_thread(process_id, one_list,transcript_dict)
	l.append(process_out)


def mutil_process(input_lines,transcript_dict):
	from multiprocessing import Manager, Process
	print("###  数据总量：", len(input_lines))
	if len(input_lines) == 0:
		print("#####   数据有问题！")
		exit()
	# 生成Manager对象
	manager = Manager()
	l = manager.list()
	thread = 39
	each_len = len(input_lines) / thread
	p_list = []
	for i in range(thread):
		if i == thread - 1:
			p = Process(target=run_function,
						args=(i, input_lines, int(each_len * i), len(input_lines), l, transcript_dict ))
		else:
			p = Process(target=run_function,
						args=(i, input_lines, int(each_len * i), int(each_len * (i + 1)), l ,transcript_dict))
		p.start()
		p_list.append(p)
	for res in p_list:
		res.join()

	json_lines = []
	total_sec = 0.0
	total_text = 0.0
	total_num = 0
	for one_l in l:
		json_lines = json_lines + one_l[0]
		total_sec = total_sec + one_l[1]
		total_text = total_text + one_l[2]
		total_num = total_num + one_l[3]

	return [json_lines, total_sec, total_text, total_num]


####  多进程处理
def create_manifest(data_dir,data_label_dir, manifest_path_prefix):
	print("Creating manifest %s ..." % manifest_path_prefix)
	json_lines = []
	transcript_path = os.path.join(data_label_dir)
	transcript_dict = {}
	f_file = codecs.open(transcript_path, 'r', 'utf-8')
	for i, line in tqdm(enumerate(f_file)):
		line = line.strip()
		if line == '':
			continue
		if '\t' in line:
			wav_name, text = line.split('\t', 1)
		else:
			wav_name, text = line.split(' ', 1)
		audio_id = wav_name.replace(".wav","")
		# remove withespace, charactor text
		text = ''.join(text.split())
		transcript_dict[audio_id] = text

	if os.path.isfile(data_dir):
		all_wav_path = read_files(data_dir)
	else:
		audio_dir = os.path.join(data_dir)
		all_wav_path = []
		for subfolder, _, filelist in tqdm(sorted(os.walk(audio_dir))):
			for fname in filelist:
				if ".wav" in fname:
					audio_path = os.path.abspath(os.path.join(subfolder, fname))
					all_wav_path.append(audio_path)
	####  打乱顺序
	random.shuffle(all_wav_path)

	data_types = {'all':all_wav_path}

	for dtype in data_types.keys():
		del json_lines[:]

		result = mutil_process(data_types[dtype],transcript_dict)
		#result = mutil_thread(data_types[dtype], transcript_dict)
		json_lines = result[0]
		total_sec = result[1]
		total_text = result[2]
		total_num = result[3]


		manifest_path = os.path.join(manifest_path_prefix, 'manifest.' + dtype + ".raw")
		with codecs.open(manifest_path, 'w', 'utf-8') as fout:
			for line in json_lines:
				fout.write(line + '\n')

		# manifest_dir = os.path.dirname(manifest_path_prefix)
		meta_path = os.path.join(manifest_path_prefix, dtype + '.meta')
		with open(meta_path, 'w') as f:
			print(f"{dtype}:", file=f)
			print(f"{total_num} utts", file=f)
			print(f"{total_sec / (60 * 60)} h", file=f)
			print(f"{total_text} text", file=f)
			print(f"{total_text / total_sec} text/sec", file=f)
			print(f"{total_sec / total_num} sec/utt", file=f)



def main():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--data",
		default="/sdb/fffan/2_relevant_experiment/1_振铃音/wav_list.txt",
		type=str, help="Directory to save the dataset. (default: %(default)s)")
	parser.add_argument("--data_label",
						default="/sdb/fffan/2_relevant_experiment/1_振铃音/wav_text.txt",
						type=str, help="Directory to save the dataset. (default: %(default)s)")
	parser.add_argument("--manifest_prefix",
		default="/sdb/fffan/2_relevant_experiment/1_振铃音",
		type=str, help="Filepath prefix for output manifests. (default: %(default)s)")
	args = parser.parse_args()

	os.makedirs(args.manifest_prefix, exist_ok=True)
	#####  多进程处理数据
	create_manifest(args.data,  args.data_label, args.manifest_prefix)



if __name__ == '__main__':
	main()

#coding: utf-8
import argparse
import codecs
import json
import os
import random
from pathlib import Path
from tqdm import tqdm
import soundfile


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

########################################################################################################################
def run_function(process_id, input_list, start, end, l, transcript_dict):
	one_list = input_list[start:end]
	print("###  进程 ", str(process_id), "数据量：", len(one_list))
	print(start, end)
	total_sec = 0.0
	total_text = 0.0
	total_num = 0
	json_lines = []
	for one_audio_path in tqdm(one_list, desc="进程" + str(process_id) + ": "):
		audio_path = one_audio_path
		audio_id = one_audio_path.split("/")[-1].replace(".wav", "")
		# if no transcription for audio then skipped
		if audio_id not in transcript_dict:
			continue

		utt2spk = Path(audio_path).parent.name
		audio_data, samplerate = soundfile.read(audio_path)

		duration = float(len(audio_data) / samplerate)
		text = transcript_dict[audio_id]
		json_lines.append(
			json.dumps(
				{
					'utt': audio_id,
					'utt2spk': str(utt2spk),
					'feat': audio_path,
					'feat_shape': (duration,),  # second
					'text': text
				},
				ensure_ascii=False))
		total_sec += duration
		total_text += len(text)
		total_num += 1
	l.append([json_lines,total_sec, total_text,total_num ])


def mutil_process(input_lines,transcript_dict, process_num):
	from multiprocessing import Manager, Process
	print("###  数据总量：", len(input_lines))
	if len(input_lines) == 0:
		print("#####   数据有问题！")
		exit()
	# 生成Manager对象
	manager = Manager()
	l = manager.list()
	thread = process_num
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
def create_manifest(data_dir,data_label_dir, manifest_path_prefix,data_type, process_num):
	print("Creating manifest %s ..." % manifest_path_prefix)
	json_lines = []
	transcript_path = os.path.join(data_label_dir)
	transcript_dict = {}
	text_f = codecs.open(transcript_path, 'r', 'utf-8')
	for line in tqdm(text_f,desc="文本加载: "):
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
	print("###  文本数据加载完成！")
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
	print("###  语音数据加载完成！",len(all_wav_path))
	##########   text 和 wav 对齐
	wav_dict = {}
	for one_wav in all_wav_path:
		name = one_wav.split("/")[-1].replace(".wav","")
		wav_dict[name] = one_wav
	all_wav_path = []
	#
	new_transcript_dict = {}
	wav_name_list = list(set(list(wav_dict.keys()))&set(list(transcript_dict.keys())))
	new_wav_path = [wav_dict[one_wav] for one_wav in wav_name_list]
	for one_wav in wav_name_list:
		new_transcript_dict[one_wav] = transcript_dict[one_wav]
	print("####  数据对齐完成！总数据：",len(wav_name_list))
	transcript_dict = {}
	###############
	all_wav_path = new_wav_path
	transcript_dict = new_transcript_dict
	###########
	####  打乱顺序
	random.shuffle(all_wav_path)

	data_types = {str(data_type): all_wav_path}
	print(len(all_wav_path))

	for dtype in data_types.keys():
		del json_lines[:]

		result = mutil_process(data_types[dtype],transcript_dict, process_num)
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


####  单进程处理
def create_manifest_single(data_dir,data_label_dir, manifest_path_prefix):
	print("Creating manifest %s ..." % manifest_path_prefix)
	json_lines = []
	transcript_path = os.path.join(data_label_dir)
	transcript_dict = {}
	for line in codecs.open(transcript_path, 'r', 'utf-8'):
		line = line.strip()
		if line == '':
			continue
		audio_id, text = line.split('\t', 1)
		# remove withespace, charactor text
		text = ''.join(text.split())
		transcript_dict[audio_id] = text

	audio_dir = os.path.join(data_dir)
	all_wav_path = []
	for subfolder, _, filelist in tqdm(sorted(os.walk(audio_dir))):
		for fname in filelist:
			if ".wav" in fname:
				audio_path = os.path.abspath(os.path.join(subfolder, fname))
				all_wav_path.append(audio_path)


	train_num = int(len(all_wav_path)*0.8)
	test_num = int(len(all_wav_path)*0.1)
	train_list = all_wav_path[:train_num]
	test_list = all_wav_path[train_num:train_num+test_num]
	dev_list = all_wav_path[train_num + test_num:]
	data_types = {'train':train_list, 'dev':dev_list, 'test':test_list}
	print(len(train_list),len(test_list),len(dev_list))
	for dtype in data_types.keys():
		del json_lines[:]
		total_sec = 0.0
		total_text = 0.0
		total_num = 0

		for one_audio_path in tqdm(data_types[dtype]):
			audio_path = one_audio_path
			audio_id = one_audio_path.split("/")[-1].replace(".wav","")
			# if no transcription for audio then skipped
			if audio_id not in transcript_dict:
				continue

			utt2spk = Path(audio_path).parent.name
			audio_data, samplerate = soundfile.read(audio_path)

			duration = float(len(audio_data) / samplerate)
			text = transcript_dict[audio_id]
			json_lines.append(
				json.dumps(
					{
						'utt': audio_id,
						'utt2spk': str(utt2spk),
						'feat': audio_path,
						'feat_shape': (duration,),  # second
						'text': text
					},
					ensure_ascii=False))
			total_sec += duration
			total_text += len(text)
			total_num += 1

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
		default="",
		type=str, help="Directory to save the dataset. (default: %(default)s)")
	parser.add_argument("--data_label",
						default="/sdb/fffan/0_data/1_resample_data/16k_wav/wespeech/text.txt",
						type=str, help="Directory to save the dataset. (default: %(default)s)")
	parser.add_argument("--manifest_prefix",
		default="./data_1025",
		type=str, help="Filepath prefix for output manifests. (default: %(default)s)")
	parser.add_argument("--data_type",
						default="",type=str, help="")
	parser.add_argument("--process_num",
						default=35, type=int, help="")
	args = parser.parse_args()

	os.makedirs(args.manifest_prefix, exist_ok=True)
	#####  多进程处理数据
	create_manifest(args.data,  args.data_label, args.manifest_prefix, args.data_type, args.process_num)

	####  单进程处理数据
	#create_manifest_single(args.data,  args.data_label, args.manifest_prefix)


if __name__ == '__main__':
	main()

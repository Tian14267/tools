import os
import pickle
import json
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
			line = line + "\n"
			f.write(line)
	f.close()


def main():
	###   获取之前的数据信息
	old_data_path = "/data/TrainSegWav/8k/CrudeTrans"
	old_data_name_list = ['onlinedata_20221012','onlinedata_20220923','onlinedata_20221017','onlinedata_20221024',
	                      'onlinedata_20221031','onlinedata_20221115']
	all_old_wavs = []
	for one_name in tqdm(old_data_name_list):
		old_path = os.path.join(old_data_path,one_name)
		for subfolder, _, filelist in tqdm(sorted(os.walk(old_path))):
			for fname in filelist:
				if ".wav" in fname:
					audio_path = os.path.abspath(os.path.join(subfolder, fname))
					all_old_wavs.append(audio_path)
	#######
	all_old_names = []
	for wav_name in tqdm(all_old_wavs):
		wav_name = wav_name.split("_crude_")[0]
		all_old_names.append(wav_name)
	all_old_names = list(set(all_old_names))

	###################################################################################################
	print(all_old_names[-1])
	print("###  old wav num: ",len(all_old_names))
	###################################################################################################
	###################################################################################################
	####  最新数据信息
	#line_new = read_files("/ultra/fffan/1_data/asr_original_data/0_线上_data/2_数据重命名/data_1017/dingzhong_new/all.txt")
	line_new = []
	for path, dir_list, file_list in os.walk("./data_2/2_resample_data_1130_zyss"):
		for file_name in file_list:
			if ".wav" in file_name:
				line_new.append(os.path.join(path, file_name))
	###############
	new_wav_dict = {}
	for one_file in line_new:
		wav_name = one_file.split("/")[-1].replace(".wav","")
		#new_wav_list.append(wav_name)
		new_wav_dict[wav_name] = one_file
	print(list(new_wav_dict.keys())[0])
	print("####  最新数据量：",len(list(new_wav_dict.keys())))
	list_out = list(set(list(new_wav_dict.keys()))-set(all_old_names))
	print("####  去重后数据量：",len(list_out))
	out_path = "./data_2/3_data_select_1130_zyss"
	os.makedirs(out_path, exist_ok=True)
	for one_wav in tqdm(list_out):
		one_wav_path = new_wav_dict[one_wav]
		wav_out = "cp " + one_wav_path + " " + out_path
		#print(wav_out)
		os.system(wav_out)


if __name__ == "__main__":
	main()
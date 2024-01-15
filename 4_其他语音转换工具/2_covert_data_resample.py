import os
import pickle
import wave
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


def check_data(wav_path):
	f = wave.open(wav_path, "rb")
	Channels = f.getnchannels()
	SampleRate = f.getframerate()
	frames = f.getnframes() ###
	Duration = frames / float(SampleRate)
	return Channels,SampleRate


def get_left_right_wav(one_file,file_name, left_path, right_path):
	wav_name = one_file.split("/")[-1].replace(".wav","")
	###  Rename
	wav_name = wav_name.replace("-","")
	#wav_split = wav_name.split("/")[-1].split("_")
	wav_split = wav_name.split("_")

	if "dz" in wav_split[0]:
		wav_name = wav_split[0] + "_8k_" + "_".join(wav_split[1:])
	else:
		wav_name = file_name+"_8k_"+wav_name
	### 提取左声道
	left_wav_path = os.path.join(left_path,wav_name+"_left.wav")
	######
	left_wav_covert = "sox " +one_file + " "+ left_wav_path+" remix 1"
	###########     channel

	#os.system(left_wav_covert)
	#### 提取右声道
	right_wav_path = os.path.join(right_path, wav_name+"_right.wav")
	right_wav_covert = "sox " + one_file + " " + right_wav_path + " remix 2"
	#print(right_wav_covert)
	#os.system(right_wav_covert)
	return left_wav_covert, right_wav_covert


def copy_file():
	original_data = ""
	wav_txt_file = ""
	target_file = ""

	wav_txt_lines = read_files(wav_txt_file)
	all_names = []
	for one_line in wav_txt_lines:
		name = one_line.split("\t")[0]
		all_names.append(name)

	for one_name in tqdm(all_names):
		line = "cp "+ os.path.join(original_data,one_name) + " " + target_file
		print(line)
		#os.system(line)



def main():
	#####  获取数据
	original_wav_path = "./data_2/1_channel_data_1205_ssld/"
	resample_rate = 8000   ####  默认 8k
	#################################
	all_mel_file_list = []
	for path, dir_list, file_list in os.walk(original_wav_path):
		for file_name in file_list:
			if ".wav" in file_name:
				all_mel_file_list.append(os.path.join(path, file_name))
	###############
	##  获取语音信息
	output_path = "./data_2/2_resample_data_1205_ssld"
	os.makedirs(output_path, exist_ok=True)
	wav_resample_list = []
	wav_copy_list = []
	file_name = "ssld"
	for one_wav in tqdm(all_mel_file_list):
		####  判断是否是鼎众数据
		###  鼎众数据是单通道数据，其他双通道数据，默认右通道是机器人声，需要过滤
		if file_name !='dz' and "right" in one_wav:
			continue
		channels, sample = check_data(one_wav)
		###
		wav_name = one_wav.split("/")[-1].replace("-", "_").replace("+86", "")
		if "_8k_" in wav_name:
			if file_name not in wav_name:
				new_name = file_name+"_"+wav_name
			else:
				new_name =  wav_name
		else:
			if file_name not in wav_name:
				wav_name = file_name + "_" + wav_name
			wav_name_split = wav_name.split("_")
			new_name = wav_name_split[0] + "_8k_" + "_".join(wav_name_split[1:])


		##
		if sample != resample_rate:
			line = "sox " + one_wav+" -r 8000 " + os.path.join(output_path,new_name)
			wav_resample_list.append(line)
			#print(line)
			#os.system(line)
		else:
			cp_line = "cp "+ one_wav +" "+os.path.join(output_path,new_name)
			wav_copy_list.append(cp_line)

	if wav_resample_list:
		print(len(wav_resample_list))
		print(wav_resample_list[0])
	if wav_copy_list:
		print(len(wav_copy_list))
		print(wav_copy_list[0])

	for one_line in tqdm(wav_copy_list+wav_resample_list):
		os.system(one_line)



if __name__ == "__main__":
	main()
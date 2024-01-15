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

	#if "dz" in wav_split[0]:
	if file_name in wav_split[0]:
		#wav_name = wav_split[0] + "_8k_" + "_".join(wav_split[1:])
		wav_name = wav_name
	else:
		#wav_name = file_name+"_8k_"+wav_name
		wav_name = file_name + "_"+wav_name
	### 提取左声道
	left_wav_path = os.path.join(left_path,wav_name+"_left.wav")
	######
	left_wav_covert = "sox " +one_file + " "+ left_wav_path+" remix 1"
	###########     channel

	#os.system(left_wav_covert)
	#### 提取右声道
	right_wav_path = os.path.join(right_path, wav_name+"_right.wav")
	right_wav_covert = "sox " + one_file + " " + right_wav_path + " remix 2"
	#print(left_wav_covert)
	#print(right_wav_covert)
	#exit()
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
	original_wav_path = "./data_out/0_select_data_dingzhong_RR_"
	#original_mp3_wav_path = "/ultra/fffan/1_data/asr_original_data/0_线上_data/9_tools/7_get_online_data/dingzhong/data_year21month9_year22month9/mp3_to_wav"
	######
	######
	all_mel_file_list = []
	for path, dir_list, file_list in os.walk(original_wav_path):
		for file_name in file_list:
			if ".wav" in file_name:
				all_mel_file_list.append(os.path.join(path, file_name))
	print("####  总数据量：",len(all_mel_file_list))
	###############
	###############
	##  获取语音信息
	left_path_list = []
	right_path_list = []
	lines = []
	###
	###  双通道转换单通道
	left_path = "./data_out/1_channel_data_dzrr_/left"
	right_path = "./data_out/1_channel_data_dzrr_/right"
	one_channel_path = "./data_out/1_channel_data_dzrr_/one_channel"
	os.makedirs(left_path, exist_ok=True)
	os.makedirs(right_path, exist_ok=True)
	os.makedirs(one_channel_path, exist_ok=True)
	###
	error_list = []
	for one_wav in all_mel_file_list:
		#file_name = one_wav.split("/")[-2]
		file_name = "dzrr"
		try:
			channels, sample = check_data(one_wav)
			if channels>1:
				left_wav, right_wav = get_left_right_wav(one_wav, file_name,left_path, right_path)
				#print(left_wav)
				#print(right_wav)
				#exit()
				left_path_list.append(left_wav)
				right_path_list.append(right_wav)
			else:
				wav_name = one_wav.split("/")[-1]
				wav_name = wav_name.replace("-","_").replace("+86","")
				wav_split = wav_name.split("_")
				if file_name in wav_split[0]:
					wav_name = wav_name
				else:
					wav_name = file_name + "_" + wav_name
				#new_wav = file_name + "_"+wav_name
				line = os.path.join(one_channel_path,wav_name)
				#print(line)
				#exit()
				lines.append("cp "+one_wav+" "+line)
		except:
			error_list.append(one_wav)

	print("### sox num: ",len(left_path_list+right_path_list))
	for one_file in tqdm(left_path_list+right_path_list):
		os.system(one_file)
	print("### copy num:",len(lines))
	for one_file in tqdm(lines):
		os.system(one_file)
	print("###  error num: ",error_list)





if __name__ == "__main__":
	main()
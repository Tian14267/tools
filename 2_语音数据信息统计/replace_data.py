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

#######################################################################################################################################################

def main():
	lines = read_files("/sdb/fffan/0_data/1_resample_data/16k_wav/wespeech/text")
	new_lines = []
	for one_line in tqdm(lines):
		new_one_line = one_line.replace("-", "_").replace("+86", "").replace("_8k_", "_16k_")
		#new_one_line = one_line.replace("audio_apth","audio_path")
		new_lines.append(new_one_line)

	write_file(new_lines,"/sdb/fffan/0_data/1_resample_data/16k_wav/wespeech/text_2")

if __name__ == "__main__":
	main()
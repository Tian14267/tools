import os
from tqdm import tqdm


def read_folder(mp3_folder, wav_folder):
	'''
	文件夹读取函数
	:param mp3_folder:
	:param wav_folder:
	:return:
	'''
	# 遍历需要转换的MP3文件夹中的MP3文件
	all_mp3_list = []
	for a in os.listdir(mp3_folder):
		# 创建MP3文件的绝对路径
		mp3_file = os.path.join(mp3_folder, a)
		all_mp3_list.append(mp3_file)
	print(len(all_mp3_list))
	for mp3_file in tqdm(all_mp3_list):
		# 调用格式转换函数
		trans_to_wav(mp3_file, wav_folder)

def trans_to_wav(mp3_file, wav_folder):
	'''
	格式转换格式
	:param amr_file:
	:param wav_folder:
	:return:
	'''

	name = mp3_file.split("/")[-1].split(".mp3")[0]
	out_file = os.path.join(wav_folder,name+".wav").replace("-","_").replace("+86","")

	line = "ffmpeg -i "+mp3_file+" "+out_file

	print('执行CMDER 命令：{}'.format(line))
	os.system(line)

if __name__ == '__main__':
	'''
	主函数入口
	'''
	# 调用文件夹读取批量文件
	mp3_folder = "/root/yshj/dz-cs-double-channel/two-c"
	wav_folder = "./mp3_to_wav"
	os.makedirs(wav_folder, exist_ok=True)
	read_folder(mp3_folder, wav_folder)


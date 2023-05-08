#!/user/bin/env python
# coding=utf-8
"""
@project : 
@author  : fffan
@time   : 2023-05-08 10:38:53
"""
import os
### pip install moviepy
from moviepy.editor import *



def do_cut_move():
	#
	# oldPath="../images/video/1.mp4"
	oldPath="./aaa/meeting_03.mp4"

	# outputfile='video42.avi'
	video = VideoFileClip(oldPath)
	# 剪辑视频，截取视频60秒
	startTime=6286
	video = video.subclip(startTime, 6511)
	video.write_videofile("clip.mp4")
	# 获取其中音频
	#audio = video.audio
	# 保存音频文件
	#audio.write_audiofile('audio.mp3')



def main():
	do_cut_move()

if __name__ == '__main__':
	main()
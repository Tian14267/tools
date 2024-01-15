# -*- coding:utf-8 -*-
import os
import time
import json
import random
import numpy as np




########  需要手动更新
time_info = [
'【首包时延】：ZPr!Zj!guW7!b!tgDDBy | 207.23676681518555ms',
'【首包时延】：xiRQvmaz0QpCz*LWo0d5 | 226.98187828063965ms',
'【首包时延】：B@5J@R57eDP$HvJHOq#C | 243.64781379699707ms',
'【尾包延迟】：xiRQvmaz0QpCz*LWo0d5 | 2115.896224975586ms',
'【RTF】：xiRQvmaz0QpCz*LWo0d5 | 0.2359869219943516 ，识别时长=2119.1625595092773 ms，音频时长=8980.0 ms',
'【尾包延迟】：B@5J@R57eDP$HvJHOq#C | 2210.887908935547ms',
'【RTF】：B@5J@R57eDP$HvJHOq#C | 0.24656843236400713 ，识别时长=2214.184522628784 ms，音频时长=8980.0 ms',

'【尾包延迟】：ZPr!Zj!guW7!b!tgDDBy | 2226.388931274414ms',
'【RTF】：ZPr!Zj!guW7!b!tgDDBy | 0.24828610813166357 ，识别时长=2229.609251022339 ms，音频时长=8980.0 ms',
'【首包时延】：aIrH*3W2g16#dQIpN0!% | 189.78190422058105ms',
'【首包时延】：kRa9X1A5VvbqKO5jAc(# | 197.5383758544922ms',
'【首包时延】：KLYw@YCkWhopOrS$jIW( | 214.57290649414062ms',
'【尾包延迟】：KLYw@YCkWhopOrS$jIW( | 2202.3959159851074ms',
'【RTF】：KLYw@YCkWhopOrS$jIW( | 0.24541287220400532 ，识别时长=2203.807592391968 ms，音频时长=8980.0 ms',

'【尾包延迟】：aIrH*3W2g16#dQIpN0!% | 2262.085437774658ms',
'【RTF】：aIrH*3W2g16#dQIpN0!% | 0.2521129121759156 ，识别时长=2263.9739513397217 ms，音频时长=8980.0 ms',

'【尾包延迟】：kRa9X1A5VvbqKO5jAc(# | 2318.25590133667ms',
'【RTF】：kRa9X1A5VvbqKO5jAc(# | 0.2584970608054928 ，识别时长=2321.303606033325 ms，音频时长=8980.0 ms',
'【首包时延】：CcI$FCZ40YIPPO)L1ahz | 184.60750579833984ms',
'【首包时延】：blN%qMQsJJeif4BGDXXA | 220.7813262939453ms',
'【首包时延】：XRULpR(i3GSmEwyxpIVW | 233.2601547241211ms',
'【尾包延迟】：CcI$FCZ40YIPPO)L1ahz | 2101.8340587615967ms',
'【RTF】：CcI$FCZ40YIPPO)L1ahz | 0.2343903936628244 ，识别时长=2104.825735092163 ms，音频时长=8980.0 ms',
'【尾包延迟】：blN%qMQsJJeif4BGDXXA | 2145.920515060425ms',
'【RTF】：blN%qMQsJJeif4BGDXXA | 0.23930048889466013 ，识别时长=2148.918390274048 ms，音频时长=8980.0 ms',
'【尾包延迟】：XRULpR(i3GSmEwyxpIVW | 2183.443307876587ms',
'【RTF】：XRULpR(i3GSmEwyxpIVW | 0.24350942641430284 ，识别时长=2186.7146492004395 ms，音频时长=8980.0 ms',



]





def main():
	time_info_static = {}
	Shoubao = []
	Weibao = []
	rtf_list = []
	asr_list = []
	for one_info in time_info:
		####  首包时延：
		if "【首包时延】" in one_info:
			shoubao_time = float(one_info.split("|")[-1].replace(" ","").replace("ms",""))
			Shoubao.append(shoubao_time)
		####  尾包时延
		if "【尾包延迟】" in one_info:
			weibao_time = float(one_info.split("|")[-1].replace(" ","").replace("ms",""))
			Weibao.append(weibao_time)
		#### RTF
		if "【RTF】" in one_info:
			rtf_time = float(one_info.split("|")[-1].split("，")[0].replace(" ","").replace("ms",""))
			rtf_list.append(rtf_time)

		if "识别时长" in one_info:
			asr_time = float(one_info.split("|")[-1].split("，")[1].split("=")[1].replace(" ", "").replace("ms", ""))
			asr_list.append(asr_time)

	print("首包数量：",len(Shoubao),"首包最小时延: ",min(Shoubao),"首包最大时延: ",max(Shoubao),"首包平均时延: ",sum(Shoubao)/len(Shoubao))
	print("尾包数量：",len(Weibao),"尾包最小时延: ",min(Weibao),"尾包最大时延: ",max(Weibao),"尾包平均时延: ", sum(Weibao) / len(Weibao))
	print("最小RTF: ",min(rtf_list)*1000,"最大RTF: ",max(rtf_list)*1000, "平均RTF: ", sum(rtf_list)*1000 / len(rtf_list))
	print("最小识别耗时: ", min(asr_list), "最大识别耗时: ", max(asr_list), "平均识别耗时: ", sum(asr_list) / len(asr_list))
	print("########################################################################")



if __name__ == "__main__":
	main()

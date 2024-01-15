#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import random
import string
import time
import threading
import multiprocessing
import wave
import websocket
from threadpool import ThreadPool, makeRequests
from urllib3.connectionpool import xrange


######  信息记录

WS_URL = "ws://0.0.0.0:10044/"  ## ASR 8k 流式接口

# 定义进程数
processes = 1
# 定义线程数
thread_num = 1

####  测试语音信息
test_wav = './Call_1002_recorded_on_5_13_2015_clt_0001_8k.wav'  ###  语音路径

###  是否输出识别结果
###如果只需要统计 首包时延、尾包延迟、RTF，设置 False
### 如果需要查看识别结果，设置 True
result_out = True
#######################################################################

last_chunk_timestamp = {}
start_timestamp = {}
first_ch_timestamp = {}
data_send_num = {}
data_rec_num = {}
last_ch_timestamp = {}

# 音频时长
wav_duration = {}
# 识别时长
rec_duration = {}

def generate_random_taskid(length):
    # string.ascii_letters 大小写字母， string.digits 为数字
    characters_long = list(string.ascii_letters + string.digits + "!@#$%^&*()")
    # 打乱字符串序列
    random.shuffle(characters_long)
    task_id_str = []
    # 生成个数
    for b in range(length):
        task_id_str.append(random.choice(characters_long))
    # 打乱顺序
    random.shuffle(task_id_str)
    # 将列表转换为字符串并打印
    return "".join(task_id_str)


def on_message(ws, message):
    endtime = time.time()
    ms_json = json.loads(message.replace("\'", "\""))
    if result_out:
        print("ms json is {}".format(ms_json))
    event_type = ms_json['event_type']
    task_id = ms_json['task_id']


    if event_type == 'PARTIAL_RESULT' and (task_id not in first_ch_timestamp):
        first_ch_timestamp[task_id] = endtime
        wb_timecost = (first_ch_timestamp[task_id] - start_timestamp[task_id]) * 1000.0
        print("\'【首包时延】：" + str(task_id) + ' | ' + str(wb_timecost) + 'ms\',')


    if event_type == 'FINAL_RESULT' and (task_id not in last_ch_timestamp):
        #print(1)
        last_ch_timestamp[task_id] = endtime
        #print(endtime)
        wb_timecost = (last_ch_timestamp[task_id] - last_chunk_timestamp[task_id]) * 1000.0
        #print("wb_webcost {}".format(wb_timecost))
        print("\'【尾包延迟】：" + str(task_id) + ' | ' + str(wb_timecost) + 'ms\',')

        rec_duration[task_id] = (last_ch_timestamp[task_id] - start_timestamp[task_id]) * 1000.0
        rec_dur = rec_duration[task_id]
        wav_dur = wav_duration[task_id]

        rtf = rec_dur * 1.0 / wav_dur
        print(
            "\'【RTF】：" + str(task_id) + " | " + str(rtf) + " ，识别时长=" + str(rec_dur) + " ms，音频时长=" + str(wav_dur) + " ms\',")


def on_error(ws, error):
    print(error)


def on_close(ws, nn, n):
    #print("####### on_close #######")
    #print(ws.url)
    #print("####### closed #######")
    pass


def on_open(ws):
    def task_run():

        # 设置websocket的内容
        # 生成TaskId
        task_id = generate_random_taskid(20)

        # 输入
        ws.send(
            '{"signal":"START","task_id":"'+ task_id +'","nbest_num":1,"continuous_decoding":true,"enable_intermediate_result":true}')

        ####  读取语音
        fin = wave.open(test_wav)
        data = fin.readframes(fin.getnframes())

        # 记录音频时长
        wav_dur = fin.getnframes() * 1.0 / 8
        wav_duration[task_id] = wav_dur
        ####  8k采样率，0.5秒的chunk
        interval = int(0.5 * 8000)
        chunk_num= 0
        for i in range(0, len(data), interval):
            chunk_num = chunk_num + 1
            chunk = data[i: min(i + interval, len(data))]
            ws.send(chunk, websocket.ABNF.OPCODE_BINARY)
            #if chunk_num > 30:
            #    break

            if i == 0:
                # 首包时间
                start_timestamp[task_id] = time.time()
        # 尾包时间
        last_chunk_timestamp[task_id] = time.time()
        #####  end
        ws.send('{"signal":"END","task_id":"' + task_id + '"}')
        

        # time.sleep(100)

    t = threading.Thread(target=task_run)
    t.start()


def on_start(num):
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(WS_URL, on_message=on_message, on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()


def thread_web_socket(p_id):
    # 线程池
    pool = ThreadPool(thread_num)
    num = list()
    # 设置开启线程的数量
    for ir in range(thread_num):
        num.append(p_id * 10000 + ir)
    requests = makeRequests(on_start, num)
    [pool.putRequest(req) for req in requests]
    pool.wait()


if __name__ == "__main__":
    starttime = time.time()
    # 进程池
    pool = multiprocessing.Pool(processes=processes)
    # 设置开启进程的数量
    for pid in xrange(processes):
        pool.apply_async(thread_web_socket, {pid})
    pool.close()
    pool.join()
    endtime = time.time()
    time_cost = (endtime - starttime) * 1000
    print(WS_URL + "，耗时：%s ms" % (time_cost))
    requests_num = thread_num * processes
    qps = (requests_num / time_cost) * 1000
    #print("【QPS】：" + str(qps))

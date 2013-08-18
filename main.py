# -*- coding: utf-8 -*-
from threading import Thread, Lock
import os, sys
from baidu_map import GeoCoding, InvGeoCoding
from helper import *

threadCount = 10

class Input:
    def __init__(self, filename):
        self.line_offset = []
        self.file = open(filename, "r")
        self.lock = Lock()
        offset = 0
        for line in self.file:
            self.line_offset.append(offset)
            offset += len(line)
    
    def Readline(self, linum):
        self.lock.acquire()
        self.file.seek(self.line_offset[linum])
        ret = self.file.readline().strip()
        self.lock.release()
        return ret

    def Size(self):
        return len(self.line_offset)

    def Close(self):
        self.lock.acquire()
        self.file.close()
        self.lock.release()

class Output:
    def __init__(self, filename):
        self.file = open(filename, "w")
        self.lock = Lock()

    def Writeline(self, value):
        self.lock.acquire()
        self.file.write(value + os.linesep)
        self.lock.release()

    def Close(self):
        self.lock.acquire()
        self.file.close()
        self.lock.release()


queue_now = 0
queue_task = 0
queue_lock = Lock() 
def thread_func(input_file, good_file, bad_file, log_file):
    global queue_now
    while True:
        queue_lock.acquire()
        if queue_now >= queue_task:
            queue_lock.release()
            break

        linum = queue_now
        queue_now += 1
        queue_lock.release()

        addr_input = input_file.Readline(linum).decode('utf-8')
        addr_input = remove_spaces_utf8(addr_input)
        addr = traditional_to_simple(addr_input)

        if len(addr) == 0:
            continue

        geoCoding = GeoCoding(addr)
        if geoCoding.GetStats() != 0:
            print "error:", geoCoding.GetStats(), addr_input
            log_file.Writeline(linum)
            break
        elif geoCoding.GetConfidence() <= 50:
            bad_file.Writeline(addr_input.encode('utf8'))
            continue

        lat, lng = geoCoding.GetLatlng()
        invGeoCoding = InvGeoCoding(lat, lng)
        if invGeoCoding.GetStats() != 0:
            print "error:", invGeoCoding.GetStats(), addr_input
            log_file.Writeline(linum)
            break

        space = u" "
        temps = invGeoCoding.GetProvince() + space +\
            invGeoCoding.GetCity() + space +\
            invGeoCoding.GetBigDistrict() + space +\
            invGeoCoding.GetSmallDistrict() + space +\
            invGeoCoding.GetFormattedAddr()
        s = simple_to_traditional(temps) + space + addr_input
        s = s.encode('utf8')
        good_file.Writeline(s)


def check_log(logDir):
    ret = 0
    try: 
        logFile = Input(logDir)
        if logFile.Size() != 0:
            ret = -1
            print u"仍有错误日志,请查看"
        logFile.Close()
    except Exception:
        None
    return ret

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print u"未提供处理文件路经参数"
        sys.exit(1)
    
    inputDir = sys.argv[1]
    words = inputDir.split('.')
    goodDir = words[0] + '_good.txt'
    badDir = words[0] + '_bad.txt'
    logDir = words[0] + '_log.txt'

    if check_log(logDir) != 0:
        print u'错误文件仍存在,请查看'
        sys.exit(2)

    inputFile = Input(inputDir)
    goodFile = Output(goodDir)
    badFile = Output(badDir)
    logFile = Output(logDir)
    
    queue_task = inputFile.Size()

    threadPool = []
    for i in range(threadCount):
        p = Thread(target=thread_func,
                   args=(inputFile, goodFile,
                         badFile, logFile))
        p.start()
        threadPool.append(p)

    for i in range(threadCount):
        threadPool[i].join()

    inputFile.Close()
    goodFile.Close()
    badFile.Close()
    logFile.Close()

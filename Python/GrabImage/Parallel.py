import sys
import random
import time
from multiprocessing import Process
import threading
import msvcrt
from ctypes import *
sys.path.append("../MvImport")
from MvCameraControl_class import *

synchL = 0
synchR = 0

g_bExit = False


def work_thread(cam=0, pData=0, nDataSize=0):
    stOutFrame = MV_FRAME_OUT()  
    memset(byref(stOutFrame), 0, sizeof(stOutFrame))
    while True:
        ret = cam.MV_CC_GetImageBuffer(stOutFrame, 1000)
        if None != stOutFrame.pBufAddr and 0 == ret:
            print ("get one frame: Width[%d], Height[%d], nFrameNum[%d]"  % (stOutFrame.stFrameInfo.nWidth, stOutFrame.stFrameInfo.nHeight, stOutFrame.stFrameInfo.nFrameNum))
            nRet = cam.MV_CC_FreeImageBuffer(stOutFrame)
        else:
            print ("no data[0x%x]" % ret)
        if g_bExit == True:
            break


def paraL():
    synchR = 1
    while 1: 
        if synchL != 0:
            break
        # 空循环等待
    # 开始执行取图片

def paraR():
    synchL = 1
    while 1: 
        if synchL != 0:
            break
        # 空循环等待
    # 开始执行取图片
        
     


def save_png(name):
    print(name,time.time(),'\n')
    time.sleep(random.randrange(1,5))

""" 
def save_png(handle,name,dir):
    print(name,'.png has saved in' ,dir) 
"""

def main():
    p1=Process(target=save_png,args=('p1',))
    p2=Process(target=save_png,args=('p2',))

    p1.start()
    p2.start()
    print('主进程')
if __name__=='__main__':
    main()
    

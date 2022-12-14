# -- coding: utf-8 --

import time
import sys
import threading
import msvcrt
from multiprocessing import Process

from ctypes import *
sys.path.append("../MvImport")
from MvCameraControl_class import *

g_bExit = False


paraL = 0

paraR = 0

# 为线程定义一个函数
def work_thread(cam=0, pData=0, nDataSize=0, wCam=0, filenum = 0):
    stOutFrame = MV_FRAME_OUT()
    memset(byref(stOutFrame), 0, sizeof(stOutFrame))

    global paraL
    global paraR

    while True:
        if wCam == 0:
            paraR = 1
            while True:
                if paraL !=0: break
        if wCam == 1:
            paraL = 1
            while True:
                if paraR != 0: break

        ret = cam.MV_CC_GetImageBuffer(stOutFrame, 1000)
        if None != stOutFrame.pBufAddr and 0 == ret:
            # print ("get one frame: Width[%d], Height[%d], nFrameNum[%d]"  % (stOutFrame.stFrameInfo.nWidth,
            #                                                                  stOutFrame.stFrameInfo.nHeight,
            #                                                                  stOutFrame.stFrameInfo.nFrameNum))
            #print(ctypes.cast(stOutFrame.pBufAddr, ctypes.py_object).value)
            nRet = cam.MV_CC_FreeImageBuffer(stOutFrame)
            print(wCam, "获取帧的时间", time.time())
            #复制帧信息

            if filenum < 5:
                if wCam == 0:
                    paraL = 0
                if wCam == 1:
                    paraR = 0

            stSaveParam = MV_SAVE_IMAGE_PARAM_EX()
            pDataForSaveImage = stOutFrame.stFrameInfo.nWidth * stOutFrame.stFrameInfo.nHeight * 4 + 2048
            stSaveParam.enImageType = MV_Image_Bmp
            stSaveParam.enPixelType = stOutFrame.stFrameInfo.enPixelType
            stSaveParam.nBufferSize = stOutFrame.stFrameInfo.nWidth * stOutFrame.stFrameInfo.nHeight * 4 + 2048
            stSaveParam.nWidth = stOutFrame.stFrameInfo.nWidth
            stSaveParam.nHeight = stOutFrame.stFrameInfo.nHeight
            stSaveParam.pData = stOutFrame.pBufAddr
            stSaveParam.nDataLen = stOutFrame.stFrameInfo.nFrameLen
            stSaveParam.pImageBuffer = (c_ubyte * pDataForSaveImage)()
            stSaveParam.nJpgQuality = 80
            #信息复制结束 开始转成图片
            filename = str(filenum).zfill(5)

            nRet =cam.MV_CC_SaveImageEx2(stSaveParam)
            if wCam == 0:
                file_path = filename+"L.bmp"
                filenum += 1
            else:
                file_path = filename+"R.bmp"
                filenum += 1
            file_open = open(file_path.encode('ascii'), 'wb+')
            try:
                #print("write" + file_path + " begin")
                img_buff = (c_ubyte * stSaveParam.nBufferSize)()
                cdll.msvcrt.memcpy(byref(img_buff), stSaveParam.pImageBuffer, stSaveParam.nDataLen)
                file_open.write(img_buff)
                #print("write" + file_path + " ok!", time.time())
            # except:
            #     raise Exception("save file executed failed:%s" % e.message)
            finally:
                file_open.close()
                cam.MV_CC_FreeImageBuffer(stOutFrame)
            if nRet != 0:
                print("get one frame fail, ret[0x%x]" % ret)
        else:
            print ("no data[0x%x]" % ret)
        if g_bExit == True:
            print("break",g_bExit)
            break

        if filenum > 5:
            break

if __name__ == "__main__":

    deviceList = MV_CC_DEVICE_INFO_LIST()
    tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE
    
    # ch:枚举设备 | en:Enum device
    ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
    if ret != 0:
        print ("enum devices fail! ret[0x%x]" % ret)
        sys.exit()

    if deviceList.nDeviceNum == 0:
        print ("find no device!")
        sys.exit()

    print ("Find %d devices!" % deviceList.nDeviceNum)

    for i in range(0, deviceList.nDeviceNum):
        mvcc_dev_info = cast(deviceList.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
        if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
            print ("\ngige device: [%d]" % i)
            # strModeName = ""
            # for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName:
            #     strModeName = strModeName + chr(per)
            # print ("device model name: %s" % strModeName)
            #
            # nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
            # nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
            # nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
            # nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
            # print ("current ip: %d.%d.%d.%d\n" % (nip1, nip2, nip3, nip4))
        elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
            print ("\nu3v device: [%d]" % i)
            strModeName = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName:
                if per == 0:
                    break
                strModeName = strModeName + chr(per)
            print ("device model name: %s" % strModeName)

            strSerialNumber = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                if per == 0:
                    break
                strSerialNumber = strSerialNumber + chr(per)
            print ("user serial number: %s" % strSerialNumber)

    nConnectionNumL = 0
    nConnectionNumR = 1
    # nConnectionNum = input("please input the number of the device to connect:")

    if int(nConnectionNumL) >= deviceList.nDeviceNum:
        print ("intput L error!")
        sys.exit()
    if int(nConnectionNumR) >= deviceList.nDeviceNum:
        print ("intput R error!")
        sys.exit()

    # ch:创建相机实例 | en:Creat Camera Object
    camL = MvCamera()
    camR = MvCamera()
    
    # ch:选择设备并创建句柄 | en:Select device and create handle
    stDeviceListL = cast(deviceList.pDeviceInfo[int(nConnectionNumL)], POINTER(MV_CC_DEVICE_INFO)).contents
    stDeviceListR = cast(deviceList.pDeviceInfo[int(nConnectionNumR)], POINTER(MV_CC_DEVICE_INFO)).contents

    ret = camL.MV_CC_CreateHandle(stDeviceListL)
    if ret != 0:
        print ("camL create handle fail! ret[0x%x]" % ret)
        sys.exit()
    ret = camR.MV_CC_CreateHandle(stDeviceListR)
    if ret != 0:
        print("camR create handle fail! ret[0x%x]" % ret)
        sys.exit()

    # ch:打开设备 | en:Open device
    ret = camL.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
    if ret != 0:
        print ("camL open device fail! ret[0x%x]" % ret)
        sys.exit()
    ret = camR.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
    if ret != 0:
        print("camR open device fail! ret[0x%x]" % ret)
        sys.exit()
    
    # ch:探测网络最佳包大小(只对GigE相机有效) | en:Detection network optimal package size(It only works for the GigE camera)
    # if stDeviceList.nTLayerType == MV_GIGE_DEVICE:
    #     nPacketSize = cam.MV_CC_GetOptimalPacketSize()
    #     if int(nPacketSize) > 0:
    #         ret = cam.MV_CC_SetIntValue("GevSCPSPacketSize",nPacketSize)
    #         if ret != 0:
    #             print ("Warning: Set Packet Size fail! ret[0x%x]" % ret)
    #     else:
    #         print ("Warning: Get Packet Size fail! ret[0x%x]" % nPacketSize)

    stBool = c_bool(False)
    ret =camL.MV_CC_GetBoolValue("AcquisitionFrameRateEnable", stBool)
    if ret != 0:
        print ("get AcquisitionFrameRateEnable fail! ret[0x%x]" % ret)
    ret = camR.MV_CC_GetBoolValue("AcquisitionFrameRateEnable", stBool)
    if ret != 0:
        print("get AcquisitionFrameRateEnable fail! ret[0x%x]" % ret)


    # ch:设置触发模式为off | en:Set trigger mode as off
    ret = camL.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
    if ret != 0:
        print ("set trigger mode fail! ret[0x%x]" % ret)
        sys.exit()
    ret = camR.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
    if ret != 0:
        print("set trigger mode fail! ret[0x%x]" % ret)
        sys.exit()

    # ch:开始取流 | en:Start grab image
    ret = camL.MV_CC_StartGrabbing()
    if ret != 0:
        print ("camL start grabbing fail! ret[0x%x]" % ret)
        sys.exit()
    ret = camR.MV_CC_StartGrabbing()
    if ret != 0:
        print("camR start grabbing fail! ret[0x%x]" % ret)
        sys.exit()

    try:


        hThreadHandleL = threading.Thread(target=work_thread, args=(camL, None, None, 0))
        hThreadHandleR = threading.Thread(target=work_thread, args=(camR, None, None, 1))
        hThreadHandleL.start()
        hThreadHandleR.start()


    except:
        print ("error: unable to start thread")

    print ("press a key to stop grabbing.")
    msvcrt.getch()

    g_bExit = True
    hThreadHandleL.join()
    hThreadHandleR.join()


    # ch:停止取流 | en:Stop grab image
    ret = camL.MV_CC_StopGrabbing()
    if ret != 0:
        print ("camL stop grabbing fail! ret[0x%x]" % ret)
        sys.exit()
    ret = camR.MV_CC_StopGrabbing()
    if ret != 0:
        print("camR stop grabbing fail! ret[0x%x]" % ret)
        sys.exit()


    # ch:关闭设备 | Close device
    ret = camL.MV_CC_CloseDevice()
    if ret != 0:
        print ("camL close deivce fail! ret[0x%x]" % ret)
        sys.exit()
    ret = camR.MV_CC_CloseDevice()
    if ret != 0:
        print("camR close deivce fail! ret[0x%x]" % ret)
        sys.exit()

    # ch:销毁句柄 | Destroy handle
    ret = camL.MV_CC_DestroyHandle()
    if ret != 0:
        print ("camL destroy handle fail! ret[0x%x]" % ret)
        sys.exit()
    ret = camR.MV_CC_DestroyHandle()
    if ret != 0:
        print("camR destroy handle fail! ret[0x%x]" % ret)
        sys.exit()

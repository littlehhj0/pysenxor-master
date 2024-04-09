#!/usr/bin/python
# -*- coding:utf-8 -*-

from __future__ import absolute_import, unicode_literals, division, print_function
import LD3320
import time
import config
import traceback
import threading
import RPi.GPIO as GPIO

flag_irq = 0
flag_t = 1
fp = 0

# /********************************************************************************
# function:	
                # Do the corresponding operation on the board
# ********************************************************************************/
def Board_text(Code_Val):
    if Code_Val == LD3320.CODE_CANCEL :       #Commond "cancel warning"          
        print("cancel")
    elif Code_Val == LD3320.CODE_KEY :     #Commond "an jian"
        print("22222222222")
    elif Code_Val == LD3320.CODE_FLASH:    #Commond "shan shuo"
        print("------")
    elif Code_Val == LD3320.CODE_PLAY:     #Commond "bo fang"
        Play_demo("test.mp3")

# /********************************************************************************
# function:
                # Play_mp3
# ********************************************************************************/
def Play_demo(path):
    # print("Play_demo")
    global bMp3Play
    global fp

    fp = open(path, 'rb+')       #open file
    fp.seek(0, 2)
    Mp3Size = fp.tell()         #file size
    fp.seek(0, 0)

    LD3320.bMp3Play = 1         #playing status
    LD.LD_Init_MP3()
    LD.LD_Adjust_Volume(5)      #adjust volume
    LD.LD_play(fp, Mp3Size)     #start play

def pthread_irq() :
    global flag_irq
    print("pthread running")
    while flag_t == 1 :
        if(GPIO.input(config.LD_IRQ) == 0) :
            flag_irq = 1
        else :
            flag_irq = 0
    print("thread:exit")

try: 
    global nAsrStatus
    global bMp3Play
    LD = LD3320.LD3320()
    print("LD3320 DEMO")
    config.module_init()
    LD.LD_init()
    
    t = threading.Thread(target = pthread_irq)
    t.setDaemon(True)
    t.start()
    nAsrRes = 0
    print(111111111111111111111111111111)
    while 1 :
        if flag_irq == 1 :
            LD.ProcessInt(fp)
        if LD3320.bMp3Play == 1 :
            # print("*********playing*********")
            continue
        if LD3320.nAsrStatus == LD3320.LD_ASR_RUNING : 
            pass
        elif LD3320.nAsrStatus == LD3320.LD_ASR_ERROR :
            pass
        elif LD3320.nAsrStatus == LD3320.LD_ASR_NONE :
            LD3320.nAsrStatus = LD3320.LD_ASR_RUNING
            if LD.LD_ASR() == 0 :                 #Start the ASR process once
                LD3320.nAsrStatus = LD3320.LD_ASR_ERROR
        elif LD3320.nAsrStatus == LD3320.LD_ASR_FOUNDOK :
            nAsrRes = LD.LD_GetResult()           #once ASR process end, get the result
            # print("Heading Code:", nAsrRes)
            if nAsrRes == LD3320.CODE_CANCEL :
                print("cancel warning")
            elif nAsrRes == LD3320.CODE_KEY :
                print("reversal led")
            elif nAsrRes == LD3320.CODE_FLASH :
                print("flash led")
            elif nAsrRes == LD3320.CODE_PLAY :
                print("play mp3")
            else :
                print("no the commond")
            LD3320.nAsrStatus = LD3320.LD_ASR_NONE
        elif LD3320.nAsrStatus == LD3320.LD_ASR_FOUNDZERO :
            LD3320.nAsrStatus = LD3320.LD_ASR_NONE
        else :
            LD3320.nAsrStatus = LD3320.LD_ASR_NONE
        Board_text(nAsrRes)
        nAsrRes = 0

except IOError as e:
    print(e)
    
except KeyboardInterrupt:
    print("ctrl + c:")
    flag_t = 0
    config.module_exit()
    t.join()
    exit()
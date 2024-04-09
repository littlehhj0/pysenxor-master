#!/usr/bin/python3
# -*- coding: utf-8 -*-
# －－－－湖南创乐博智能科技有限公司－－－－
#  文件名：30_barometer.py
#  版本：V2.0
#  author: zhulin
# 说明：BMP180气压传感器实验
#####################################################
import Adafruit_BMP.BMP085 as BMP085
import RPi.GPIO as GPIO
import time


makerobo_sensor = BMP085.BMP085()    # 实例化BMP180 对象

# 循环函数
def loop():
    while(True):
        print('Makerobo Temp = {0:0.2f} *C'.format(makerobo_sensor.read_temperature()))    # 获取温度
        print('Makerobo Pressure = {0:0.2f} Pa'.format(makerobo_sensor.read_pressure()))   # 读取气压值
        print('Makerobo Sealevel Pressure = {0:0.2f} Pa'.format(makerobo_sensor.read_sealevel_pressure()))
        time.sleep(0.5)

 # 释放资源
def destroy():
	GPIO.cleanup()                              # 释放资源

# 程序入口
if __name__ == '__main__':     
	try:
		loop()
	except KeyboardInterrupt:  # 当按下Ctrl+C时，将执行destroy()子程序。
		destroy()    # 释放资源

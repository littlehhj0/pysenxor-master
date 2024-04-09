# Copyright (C) Meridian Innovation Ltd. Hong Kong, 2020. All rights reserved.
#
import sys
import os
import signal
import time
import logging
import serial
import numpy as np
import collections
import PIL.Image as Image


import mediapipe as mp

num=0
num1=0
datainitial = [[[0]*80]*62]*12
try:
    import cv2 as cv
except:
    print("Please install OpenCV (or link existing installation)"
          " to see the thermal image")
    exit(1)

from senxor.mi48 import MI48, format_header, format_framestats
from senxor.utils import data_to_frame,RollingAverageFilter,FibonacciAverageFilter
from senxor.interfaces import get_serial, USB_Interface


list_ironbow_b = [0, 6, 12, 18, 27, 38, 49, 59, 64, 68, 73, 78, 82, 86, 90, 94, 98, 102, 105, 109, 112, 115, 119, 122,
                  124, 127, 129, 132, 134, 136, 138, 140, 142, 145, 147, 148, 150, 151, 152, 153, 154, 155, 157, 158,
                  159, 160, 161, 163, 163, 164, 165, 166, 166, 167, 167, 167, 167, 167, 166, 166, 166, 165, 165, 165,
                  165, 164, 164, 164, 163, 162, 161, 160, 160, 160, 158, 157, 156, 155, 153, 152, 151, 150, 148, 147,
                  146, 145, 143, 142, 141, 140, 138, 136, 134, 132, 130, 127, 125, 123, 121, 119, 118, 116, 114, 112,
                  110, 108, 106, 104, 102, 100, 98, 96, 94, 92, 90, 88, 86, 84, 82, 80, 78, 75, 73, 71, 69, 67, 65, 63,
                  61, 59, 57, 55, 53, 51, 49, 48, 46, 44, 42, 40, 38, 36, 34, 32, 31, 29, 27, 25, 24, 22, 21, 20, 18,
                  17, 16, 15, 13, 12, 11, 9, 8, 7, 6, 4, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 5, 6, 7, 9, 10, 12, 13, 14, 16, 17, 20, 23, 26, 28, 31, 34, 37, 39,
                  42, 45, 48, 50, 53, 56, 59, 62, 66, 70, 74, 78, 82, 86, 91, 96, 101, 106, 111, 115, 120, 125, 130,
                  135, 140, 146, 152, 158, 164, 171, 178, 185, 192, 201, 210, 219, 229, 237, 243, 248, 251, 254]
list_ironbow_g = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 3, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3,
                  4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 30, 31, 32,
                  33, 34, 35, 36, 37, 39, 40, 42, 43, 45, 47, 48, 50, 51, 53, 54, 56, 58, 59, 61, 62, 64, 65, 67, 69,
                  70, 72, 73, 75, 76, 78, 80, 81, 83, 84, 86, 88, 89, 91, 93, 95, 96, 98, 100, 102, 103, 105, 107, 109,
                  110, 112, 114, 116, 117, 119, 121, 122, 124, 126, 128, 129, 131, 133, 134, 136, 138, 139, 141, 143,
                  145, 146, 148, 150, 151, 153, 155, 156, 158, 160, 161, 163, 165, 167, 168, 170, 172, 173, 175, 177,
                  178, 180, 182, 184, 185, 187, 188, 190, 191, 193, 194, 196, 197, 199, 200, 202, 203, 205, 206, 208,
                  209, 211, 212, 214, 215, 216, 217, 219, 220, 221, 223, 224, 225, 227, 228, 229, 231, 232, 233, 235,
                  235, 236, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 249, 250, 251, 252,
                  253, 254, 255, 255, 255, 255, 255, 254, 254, 254, 254, 254]
list_ironbow_r = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 5, 9, 12, 16, 19, 23, 26, 29, 33, 36, 39, 43, 46, 49, 52,
                  54, 57, 60, 63, 66, 69, 71, 74, 77, 80, 83, 85, 88, 91, 94, 96, 99, 102, 105, 107, 110, 112, 115, 117,
                  120, 122, 124, 127, 129, 131, 133, 136, 138, 140, 142, 145, 147, 149, 151, 154, 156, 158, 160, 161,
                  163, 165, 167, 169, 170, 172, 174, 176, 178, 179, 181, 183, 185, 187, 189, 190, 192, 194, 195, 196,
                  198, 199, 201, 202, 204, 205, 206, 208, 209, 211, 212, 213, 214, 215, 216, 217, 218, 219, 221, 222,
                  223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243,
                  243, 244, 245, 245, 246, 247, 248, 248, 249, 250, 250, 251, 251, 252, 253, 253, 254, 254, 254, 254,
                  254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 255, 255, 255, 255, 255, 255,
                  255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                  255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                  255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 254, 254, 254, 253, 253,
                  252, 252, 252, 251, 251, 250, 250, 250, 250, 250, 249, 248, 247, 246, 246, 245, 245, 245, 246, 247,
                  249, 251, 254]
lut_ironbow = np.zeros((256, 1, 3), dtype=np.uint8)
lut_ironbow[:, :, 0] = np.array(list_ironbow_b).reshape(256, 1)
lut_ironbow[:, :, 1] = np.array(list_ironbow_g).reshape(256, 1)
lut_ironbow[:, :, 2] = np.array(list_ironbow_r).reshape(256, 1)

list_rainbow2 = [1, 3, 74, 0, 3, 74, 0, 3, 75, 0, 3, 75, 0, 3, 76, 0, 3, 76, 0, 3, 77, 0, 3, 79, 0, 3, 82, 0, 5, 85, 0,
                 7, 88, 0, 10, 91, 0, 14, 94, 0, 19, 98, 0, 22, 100, 0, 25, 103, 0, 28, 106, 0, 32, 109, 0, 35, 112, 0,
                 38, 116, 0, 40, 119, 0, 42, 123, 0, 45, 128, 0, 49, 133, 0, 50, 134, 0, 51, 136, 0, 52, 137, 0, 53,
                 139, 0, 54, 142, 0, 55, 144, 0, 56, 145, 0, 58, 149, 0, 61, 154, 0, 63, 156, 0, 65, 159, 0, 66, 161, 0,
                 68, 164, 0, 69, 167, 0, 71, 170, 0, 73, 174, 0, 75, 179, 0, 76, 181, 0, 78, 184, 0, 79, 187, 0, 80,
                 188, 0, 81, 190, 0, 84, 194, 0, 87, 198, 0, 88, 200, 0, 90, 203, 0, 92, 205, 0, 94, 207, 0, 94, 208, 0,
                 95, 209, 0, 96, 210, 0, 97, 211, 0, 99, 214, 0, 102, 217, 0, 103, 218, 0, 104, 219, 0, 105, 220, 0,
                 107, 221, 0, 109, 223, 0, 111, 223, 0, 113, 223, 0, 115, 222, 0, 117, 221, 0, 118, 220, 1, 120, 219, 1,
                 122, 217, 2, 124, 216, 2, 126, 214, 3, 129, 212, 3, 131, 207, 4, 132, 205, 4, 133, 202, 4, 134, 197, 5,
                 136, 192, 6, 138, 185, 7, 141, 178, 8, 142, 172, 10, 144, 166, 10, 144, 162, 11, 145, 158, 12, 146,
                 153, 13, 147, 149, 15, 149, 140, 17, 151, 132, 22, 153, 120, 25, 154, 115, 28, 156, 109, 34, 158, 101,
                 40, 160, 94, 45, 162, 86, 51, 164, 79, 59, 167, 69, 67, 171, 60, 72, 173, 54, 78, 175, 48, 83, 177, 43,
                 89, 179, 39, 93, 181, 35, 98, 183, 31, 105, 185, 26, 109, 187, 23, 113, 188, 21, 118, 189, 19, 123,
                 191, 17, 128, 193, 14, 134, 195, 12, 138, 196, 10, 142, 197, 8, 146, 198, 6, 151, 200, 5, 155, 201, 4,
                 160, 203, 3, 164, 204, 2, 169, 205, 2, 173, 206, 1, 175, 207, 1, 178, 207, 1, 184, 208, 0, 190, 210, 0,
                 193, 211, 0, 196, 212, 0, 199, 212, 0, 202, 213, 1, 207, 214, 2, 212, 215, 3, 215, 214, 3, 218, 214, 3,
                 220, 213, 3, 222, 213, 4, 224, 212, 4, 225, 212, 5, 226, 212, 5, 229, 211, 5, 232, 211, 6, 232, 211, 6,
                 233, 211, 6, 234, 210, 6, 235, 210, 7, 236, 209, 7, 237, 208, 8, 239, 206, 8, 241, 204, 9, 242, 203, 9,
                 244, 202, 10, 244, 201, 10, 245, 200, 10, 245, 199, 11, 246, 198, 11, 247, 197, 12, 248, 194, 13, 249,
                 191, 14, 250, 189, 14, 251, 187, 15, 251, 185, 16, 252, 183, 17, 252, 178, 18, 253, 174, 19, 253, 171,
                 19, 254, 168, 20, 254, 165, 21, 254, 164, 21, 255, 163, 22, 255, 161, 22, 255, 159, 23, 255, 157, 23,
                 255, 155, 24, 255, 149, 25, 255, 143, 27, 255, 139, 28, 255, 135, 30, 255, 131, 31, 255, 127, 32, 255,
                 118, 34, 255, 110, 36, 255, 104, 37, 255, 101, 38, 255, 99, 39, 255, 93, 40, 255, 88, 42, 254, 82, 43,
                 254, 77, 45, 254, 69, 47, 254, 62, 49, 253, 57, 50, 253, 53, 52, 252, 49, 53, 252, 45, 55, 251, 39, 57,
                 251, 33, 59, 251, 32, 60, 251, 31, 60, 251, 30, 61, 251, 29, 61, 251, 28, 62, 250, 27, 63, 250, 27, 65,
                 249, 26, 66, 249, 26, 68, 248, 25, 70, 248, 24, 73, 247, 24, 75, 247, 25, 77, 247, 25, 79, 247, 26, 81,
                 247, 32, 83, 247, 35, 85, 247, 38, 86, 247, 42, 88, 247, 46, 90, 247, 50, 92, 248, 55, 94, 248, 59, 96,
                 248, 64, 98, 248, 72, 101, 249, 81, 104, 249, 87, 106, 250, 93, 108, 250, 95, 109, 250, 98, 110, 250,
                 100, 111, 251, 101, 112, 251, 102, 113, 251, 109, 117, 252, 116, 121, 252, 121, 123, 253, 126, 126,
                 253, 130, 128, 254, 135, 131, 254, 139, 133, 254, 144, 136, 254, 151, 140, 255, 158, 144, 255, 163,
                 146, 255, 168, 149, 255, 173, 152, 255, 176, 153, 255, 178, 155, 255, 184, 160, 255, 191, 165, 255,
                 195, 168, 255, 199, 172, 255, 203, 175, 255, 207, 179, 255, 211, 182, 255, 216, 185, 255, 218, 190,
                 255, 220, 196, 255, 222, 200, 255, 225, 202, 255, 227, 204, 255, 230, 206, 255, 233, 208]
lut_rainbow2 = np.zeros((256, 1, 3), dtype=np.uint8)
lut_rainbow2[:, :, 0] = np.array(list_rainbow2[2::3]).reshape(256, 1)
lut_rainbow2[:, :, 1] = np.array(list_rainbow2[1::3]).reshape(256, 1)
lut_rainbow2[:, :, 2] = np.array(list_rainbow2[0::3]).reshape(256, 1)

colormaps = {
    'autumn': cv.COLORMAP_AUTUMN,
    'bone': cv.COLORMAP_BONE,
    'jet': cv.COLORMAP_JET,
    'winter': cv.COLORMAP_WINTER,
    'rainbow': cv.COLORMAP_RAINBOW,
    'ocean': cv.COLORMAP_OCEAN,
    'summer': cv.COLORMAP_SUMMER,
    'spring': cv.COLORMAP_SPRING,
    'cool': cv.COLORMAP_COOL,
    'hsv': cv.COLORMAP_HSV,
    'pink': cv.COLORMAP_PINK,
    'hot': cv.COLORMAP_HOT,
    'parula': cv.COLORMAP_PARULA,
    'magma': cv.COLORMAP_MAGMA,
    'inferno': cv.COLORMAP_INFERNO,
    'plasma': cv.COLORMAP_PLASMA,
    'viridis': cv.COLORMAP_VIRIDIS,
    'cividis': cv.COLORMAP_CIVIDIS,
    'twilight': cv.COLORMAP_TWILIGHT,
    'twilight_shifted': cv.COLORMAP_TWILIGHT_SHIFTED,
    # the following is available in 4.2 or later only
    # 'turbo': cv.COLORMAP_TURBO,
    'rainbow2': lut_rainbow2, 'ironbow': lut_ironbow[-256:],
}

def remap(data, new_range=(0, 255), curr_range=None, to_uint8=True):
    """
    Remap data from one range to another; return float16.

    This function is critical for working with temperature data and
    maintaining accuracy.

    The mapping is a linear transformation:

        l1, h1 = curr_range

        l2, h2 = new_range

        x = (data - l1) / (h1 - l1)

        out = l2 + x * (h2 - l1)

    If `curr_range` is not specified, assume it is defined by the data limits.
    If `to_uint8` is true, return an uint8, instead of float16. This is
    useful in conjuction with `new_range` being (0, 255), to prepare for
    many OpneCV routines which accept only uint8.
    """
    lo2, hi2 = new_range
    #
    if curr_range is None:
        lo1 = np.min(data)+2
        hi1 = np.max(data)
    else:
        lo1, hi1 = curr_range
    #
    # The relpos below represents the relative position of _data in the
    # current range.
    # We could potentially manipulate relpos by some function to
    # realise non-linear remapping
    relpos = (data - lo1) / float(hi1 - lo1)
    out = lo2 + relpos * (hi2 - lo2)
    #
    if to_uint8:
        return out.astype('uint8')
    else:
        return out.astype('float16')



# This will enable mi48 logging debug messages
logger = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
#

def cv_display(img, title='', resize=(320, 248),
               colormap=lut_ironbow, interpolation=cv.INTER_CUBIC):
    global datainitial
    """
    Display image using OpenCV-controled window.

    Data is a 2D numpy array of type uint8,

    Image is coloured and resized
    """
    #img = cv.bilateralFilter(img,1,23,23)
    #clahe = cv.createCLAHE(clipLimit=1, tileGridSize=(4,4))
    #img = clahe.apply(img)
    img = cv.blur(img,(3,3))
    #img = cv.GaussianBlur(img, (5,5), -5)
    img = cv.bilateralFilter(img , 5,75,75)
    img = cv.fastNlMeansDenoising(img ,5,5,11)
    
    

    cvcol = cv.applyColorMap(img, colormap)
    cvresize =  cv.resize(cvcol, resize, interpolation=interpolation)
    #cv.imshow(title, cvresize)
    if (num == 1):
        datainitial = [cvresize] *12
    if(num%2==1):
        datainitial=datainitial[1:]+[cvresize]
        #end = compound(datainitial)
        #将图像转为灰度图像
        grayscale_img = cv.cvtColor(datainitial[11], cv.COLOR_BGR2GRAY)
        # 边缘检测 
        # edges = cv.Canny(grayscale_img, 50, 30)
        img_binary = cv.threshold(grayscale_img, 128, 255, cv.THRESH_BINARY)[1]
        cv.imshow(title, img_binary)
        #path='/home/pi/Pictures/k/2/1.jpg'
        #cv.imwrite(path,end)

def compound(img):
    img_tmp1 = np.hstack((img[0],img[1],img[2]))
    img_tmp2 = np.hstack((img[3],img[4],img[5]))
    img_tmp3 = np.hstack((img[6],img[7],img[8]))
    img_tmp4 = np.hstack((img[9],img[10],img[11]))
    img= np.vstack((img_tmp1,img_tmp2,img_tmp3,img_tmp4))
   
    return img




# Make the a global variable and use it as an instance of the mi48.
# This allows it to be used directly in a signal_handler.
global mi48

# define a signal handler to ensure clean closure upon CTRL+C
# or kill from terminal
def signal_handler(sig, frame):
    """Ensure clean exit in case of SIGINT or SIGTERM"""
    logger.info("Exiting due to SIGINT or SIGTERM")
    mi48.stop()
    cv.destroyAllWindows()
    logger.info("Done.")
    sys.exit(0)

# Define the signals that should be handled to ensure clean exit
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ==============================
# create an USB interface object
# ==============================
try:
    ser = get_serial()[0]
except IndexError:
    # if on WSL (hack); apply similarly to other cases where
    # device may not be readily found by get_serial
    try:
        ser = serial.Serial('/dev/ttyS4')
    except OSError:
        ser = serial.Serial('/dev/ttyS3')
usb = USB_Interface(ser)
logger.debug('Connected USB interface:')
logger.debug(usb)

# Make an instance of the MI48, attaching USB for 
# both control and data interface.
mi48 = MI48([usb, usb])

# print out camera info
camera_info = mi48.get_camera_info()
logger.info('Camera info:')
logger.info(camera_info)

# set desired FPS

mi48.set_fps(9)


# see if filtering is available in MI48 and set it up
# see if filtering is available in MI48 and set it up

if int(mi48.fw_version[0]) >= 2:
# Enable filtering with default strengths
    mi48.enable_filter(f1=True, f2=True, f3=False, f3_ks_5=False)

# If needed, set a temperature offset across entire frame
# e.g. if overall accuracy (at product level) seems to be
# 0.7 above the blackbody, then we need to subtract 0.7
# from the readout of the MI48:
# mi48.set_offset_corr(-5.55)
#
# However, for most applications the factory level, per pixel
# calibration is sufficient, so keep offset 0
    mi48.set_offset_corr(0.0)


mi48.set_filter_1(50)
mi48.set_filter_2(4)
# initiate continuous frame acquisition
mi48.disable_low_netd()
with_header = True
mi48.start(stream=True, with_header=with_header)

# change this to false if not interested in the image
GUI = True

while True:
    data, header = mi48.read()

    if(num!=0):
        GUI=True
        if data is None:
            logger.critical('NONE data received instead of GFRA')
            mi48.stop()
            sys.exit(1)
        data = remap(data, new_range=(0, 255), curr_range=None, to_uint8=True)
        img = data_to_frame(data, mi48.fpa_shape)
  
        if header is not None:
            logger.debug('  '.join([format_header(header),
                                format_framestats(data)]))
        else:
            logger.debug(format_framestats(data))

        img8u = cv.normalize(img.astype('uint8'), None, 255, 0,
                         norm_type=cv.NORM_MINMAX,
                         dtype=cv.CV_8U)
        if GUI:

            cv_display(img8u)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break
    num+=1
#    time.sleep(1)

# stop capture and quit
mi48.stop()
cv.destroyAllWindows()

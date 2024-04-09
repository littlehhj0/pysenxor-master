# /*****************************************************************************
# * | File        :	  config.py
# * | Author      :   Waveshare team
# * | Function    :   Hardware underlying interface,for Raspberry pi
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2020-06-24
# * | Info        :   
# ******************************************************************************/
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from __future__ import absolute_import, unicode_literals, division, print_function
import RPi.GPIO as GPIO
import time
import spidev
import ctypes

#Pin definition
LD_CS   =   12
LD_WR   =   27
LD_RST  =   25
LD_IRQ  =   22

spi = spidev.SpiDev(0, 1)
spi.lsbfirst = False

def delay_ms(delaytime):
    time.sleep(delaytime / 1000.0)

def spi_send_byte(data):
    spi.xfer([data[0]])

def LD_WriteReg(data1, data2):
    GPIO.output(LD_CS, 0)
    GPIO.output(LD_WR, 0)
    spi_send_byte([0x04])
    spi_send_byte([data1])
    spi_send_byte([data2])
    # print("writereg is ", data1, data2)
    GPIO.output(LD_CS, 1)

def LD_ReadReg(reg_add):
    GPIO.output(LD_CS, 0)
    GPIO.output(LD_WR, 0)
    spi_send_byte([0x05])
    spi_send_byte([reg_add])
    i = (int)(spi.xfer([0x00])[0])
    # print("xxxxxxxxxxxxx\r\n")
    # print(i)
    GPIO.output(LD_CS, 1)
    return(i)
    
def module_init():
    print("module_init")
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(LD_RST, GPIO.OUT)
    GPIO.setup(LD_WR, GPIO.OUT)
    GPIO.setup(LD_CS, GPIO.OUT)  
    GPIO.setup(LD_IRQ, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
    spi.max_speed_hz = 10000000
    spi.mode = 2
    GPIO.output(LD_RST, 0)
    GPIO.output(LD_CS, 0)
    GPIO.output(LD_WR, 0)
    return 0

def module_exit():
    spi.close()
    GPIO.output(LD_RST, 0)
    GPIO.output(LD_WR, 0)

# /********************************************************************************
# function:
                # Hardware reset
# ********************************************************************************/
def LD_reset():
    GPIO.output(LD_RST, 1)
    delay_ms(100)
    GPIO.output(LD_RST, 0)
    delay_ms(100)
    GPIO.output(LD_RST, 1)
    
    delay_ms(100)
    GPIO.output(LD_CS, 0)
    delay_ms(100)
    GPIO.output(LD_CS, 1)
    delay_ms(100)
    
    print("LD reset over")
### END OF FILE ###

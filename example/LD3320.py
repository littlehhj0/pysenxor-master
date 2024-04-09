# /*****************************************************************************
# * | File        :	  LD3320.py
# * | Author      :   Waveshare team
# * | Function    :   Driver for LD3320
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

from __future__ import absolute_import, unicode_literals, division, print_function
import config
import RPi.GPIO as GPIO
import base64

# The following five states are defined to record which state the program is in while running ASR recognition
LD_ASR_NONE         =   0x00    #Indicates that ASR recognition is not being made
LD_ASR_RUNING       =   0x01    #Indicates that LD3320 is in ASR identification
LD_ASR_FOUNDOK      =   0x10    #Represents the end of an identification process, with an identification result
LD_ASR_FOUNDZERO    =   0x11    #Represents the end of an identification process, no identification results
LD_ASR_ERROR        =   0x31    #Represents an incorrect state occurring inside the LD3320 chip in a recognition process

#The following three states are defined to record whether the program is running ASR recognition or MP3
LD_MODE_IDLE    =   0x00
LD_MODE_ASR_RUN =   0x08
LD_MODE_MP3     =   0x40

# Identification code (Customer Modification)
CODE_CANCEL       =   1   #commond code for cancel warning
CODE_KEY        =   2   #commond code for LED flash
CODE_FLASH      =   3   #commond code for LED reversal
CODE_PLAY       =   4   #commond code for PLAY MP3

# LD chip fixed values.
RESUM_OF_MUSIC      =   0x01
CAUSE_MP3_SONG_END  =   0x20

# LD clock set
CLK_IN          =   22                      #crystal oscillator
LD_PLL_11       =   (int)((CLK_IN/2.0)-1)
LD_PLL_MP3_19   =   0x0f
LD_PLL_MP3_1B   =   0x18
LD_PLL_MP3_1D   =   (int)(((90.0*((LD_PLL_11)+1))/(CLK_IN))-1)

LD_PLL_ASR_19   =   (int)(CLK_IN*32.0/(LD_PLL_11+1) - 0.51)
LD_PLL_ASR_1B   =   0x48
LD_PLL_ASR_1D   =   0x1f

# VOL reg
MIC_VOL         =   0x43
SPEAKER_VOL     =   0x07

MASK_INT_SYNC           =   0x10
MASK_INT_FIFO           =   0x04
MASK_AFIFO_INT          =   0x01
MASK_FIFO_STATUS_AFULL  =   0x08

nMp3Size        =   0               # mp3 size
nMp3Pos         =   0               # mp3 current pos
nAsrStatus      =   0               # Record the status of the ASR	
nLD_Mode        =   LD_MODE_IDLE    # Record the status of LD3320(ASR or Play Sound)
ucStatus        =   0               # FIFO status
ucSPVol         =   15              # Speaker volume, MAX=31 MIN=0
bMp3Play        =   0               # status of play mp3


class LD3320(object):
    # /********************************************************************************
    # function:
                    # Get LD3320 return value
    # ********************************************************************************/
    def LD_GetResult(self):    
        return config.LD_ReadReg(0xc5)   

    # /********************************************************************************
    # function:
                    # Begin to ASR
    # ********************************************************************************/
    def LD_AsrRun(self):    
        config.LD_WriteReg(0x35, MIC_VOL)
        config.LD_WriteReg(0x1C, 0x09)
        config.LD_WriteReg(0xBD, 0x20)
        config.LD_WriteReg(0x08, 0x01)
        config.delay_ms(20)
        config.LD_WriteReg(0x08, 0x00)
        config.delay_ms(20)
        if(self.LD_Check_ASRBusyFlag() == 0) :
            print("AsrRun Error")
            return 0        
        config.LD_WriteReg(0xB2, 0xff)	
        config.LD_WriteReg(0x37, 0x06)
        config.LD_WriteReg(0x37, 0x06)
        config.delay_ms(20)
        config.LD_WriteReg(0x1C, 0x0b)
        config.LD_WriteReg(0x29, 0x10)
        config.LD_WriteReg(0xBD, 0x00)
        return 1

    # /********************************************************************************
    # function:
                    # Check ASR state
    # ********************************************************************************/
    def LD_Check_ASRBusyFlag(self):
        flag = 0
        for j in range (0, 5) :
            # print(config.LD_ReadReg(0xb2))
            if config.LD_ReadReg(0xb2) == 0x21 :                
                flag = 1
                break
            config.delay_ms(10)
            #print("ERROR!!! ASR Busy")
        return flag
    
    # /********************************************************************************
    # function:
                    # Common init
    # ********************************************************************************/
    def LD_Init_Common(self):
        global bMp3Play
        bMp3Play = 0
        config.LD_ReadReg(0x06)
        config.LD_WriteReg(0x17, 0x35)
        config.delay_ms(20)
        config.LD_ReadReg(0x06)

        config.LD_WriteReg(0x89, 0x03)
        config.delay_ms(20)
        config.LD_WriteReg(0xCF, 0x43)
        config.delay_ms(20)
        config.LD_WriteReg(0xCB, 0x02)
        
        # /*PLL setting*/
        config.LD_WriteReg(0x11, LD_PLL_11)
        if (nLD_Mode == LD_MODE_MP3):
            config.LD_WriteReg(0x1E, 0x00) 
            config.LD_WriteReg(0x19, LD_PLL_MP3_19)
            config.LD_WriteReg(0x1B, LD_PLL_MP3_1B)
            config.LD_WriteReg(0x1D, LD_PLL_MP3_1D)
        
        else:
            config.LD_WriteReg(0x1E,0x00)
            config.LD_WriteReg(0x19, LD_PLL_ASR_19)
            config.LD_WriteReg(0x1B, LD_PLL_ASR_1B)
            config.LD_WriteReg(0x1D, LD_PLL_ASR_1D)
        
        config.delay_ms(20)
        
        config.LD_WriteReg(0xCD, 0x04)
        config.LD_WriteReg(0x17, 0x4c) 
        config.delay_ms(20)
        config.LD_WriteReg(0xB9, 0x00)
        config.LD_WriteReg(0xCF, 0x4F) 
        config.LD_WriteReg(0x6F, 0xFF) 

    # /********************************************************************************
    # function:
                    # ASR init
    # ********************************************************************************/
    def LD_Init_ASR(self):
        global nLD_Mode
        nLD_Mode = LD_MODE_ASR_RUN
        self.LD_Init_Common()
        config.LD_WriteReg(0xBD, 0x00)
        config.LD_WriteReg(0x17, 0x48)
        config.delay_ms(20)
        
        config.LD_WriteReg(0x3C, 0x80)
        config.LD_WriteReg(0x3E, 0x07)
        config.LD_WriteReg(0x38, 0xff)
        config.LD_WriteReg(0x3A, 0x07)
        config.delay_ms(20)
        
        config.LD_WriteReg(0x40, 0x00)
        config.LD_WriteReg(0x42, 0x08)
        config.LD_WriteReg(0x44, 0x00)
        config.LD_WriteReg(0x46, 0x08)
        config.delay_ms(20)
        
    # /********************************************************************************
    # function:
                    # MP3 player init
    # ********************************************************************************/
    def LD_Init_MP3(self):    
        global nLD_Mode
        nLD_Mode = LD_MODE_MP3
        self.LD_Init_Common()

        config.LD_WriteReg(0xBD, 0x02)
        config.LD_WriteReg(0x17, 0x48)
        config.delay_ms(20)
        config.LD_WriteReg(0x85, 0x52) 
        config.LD_WriteReg(0x8F, 0x00)  
        config.LD_WriteReg(0x81, 0x00)
        config.LD_WriteReg(0x83, 0x00)
        config.LD_WriteReg(0x8E, 0xff)
        config.LD_WriteReg(0x8D, 0xff)
        config.delay_ms(20)
        config.LD_WriteReg(0x87, 0xff)
        config.LD_WriteReg(0x89, 0xff)
        config.delay_ms(20)
        config.LD_WriteReg(0x22, 0x00)
        config.LD_WriteReg(0x23, 0x00)
        config.LD_WriteReg(0x20, 0xef)
        config.LD_WriteReg(0x21, 0x07)
        config.LD_WriteReg(0x24, 0x77)
        config.LD_WriteReg(0x25, 0x03)
        config.LD_WriteReg(0x26, 0xbb)
        config.LD_WriteReg(0x27, 0x01)

    # /********************************************************************************
    # function:
                    # Adjust volume
    # note:
                    # MAX=15 MIN=0
    # ********************************************************************************/
    def LD_Adjust_Volume(self, val):
        val = ((15-val)&0x0f) << 2
        config.LD_WriteReg(0x8e, val | 0xc1)    #volume
        config.LD_WriteReg(0x87, 0x78)          #accept adjust
    
    # /********************************************************************************
    # function:	
                    # Add  ASR Key
    # ********************************************************************************/
    def LD_AsrAddKey(self):
        DATE_A = 4  

        sRecog = [              #add commond,use pinying
                "wo mei shi",\
                "an jian",\
                "shan shuo",\
                "bo fang",\

                                                                    ]
        pCode  = [              #add commond code to do the commond
                CODE_CANCEL,   \
                CODE_KEY,   \
                CODE_FLASH,\
                CODE_PLAY,\

                                                            ]
        flag = 1
        # sRecog_s = str(sRecog)
        for k in range (0, DATE_A):     #write data to LD3320
            if(self.LD_Check_ASRBusyFlag() == 0):
                flag = 0
                break               
            config.LD_WriteReg(0xc1, pCode[k])
            config.LD_WriteReg(0xc3, 0)
            config.LD_WriteReg(0x08, 0x04)
            config.delay_ms(1)
            config.LD_WriteReg(0x08, 0x00)
            config.delay_ms(1)
            sRecog_s = sRecog[k].encode(encoding='UTF-8')       #to str
            nAsrAddLength = len(sRecog_s)                       #get str lenth
            # print(sRecog_s)
            # print(nAsrAddLength)
            for i in range(0, nAsrAddLength) :
                val = sRecog_s[i]
                if isinstance(val, str) :                       #python2 val is str,python3 val is not str
                    val = ord(val)                              #char to hex
                config.LD_WriteReg(0x05, val)
            config.LD_WriteReg(0xb9, nAsrAddLength)
            config.LD_WriteReg(0xb2, 0xff)
            config.LD_WriteReg(0x37, 0x04)
        # print("LD_AsrAddKey over")
        return flag

    # /********************************************************************************
    # function:
                    # Run ASR
    # ********************************************************************************/
    def LD_ASR(self):    
        i = 0
        asrflag = 0
        for i in range(0, 10):               #run ASR try 5 times
            self.LD_Init_ASR()                   #init ASR
            config.delay_ms(100)
            if (self.LD_AsrAddKey() == 0):     #Add fixed to LD3320
                print("ERROR!!! LD_AsrAddKey")
                config.LD_reset()                  #ERROR,Reset LD3320
                config.delay_ms(50)	
                continue
            config.delay_ms(10)
            if (self.LD_AsrRun() == 0):          #start ASR
                print("ERROR!!! LD_AsrRun")
                config.LD_reset()                  #ERROR,Reset LD3320
                config.delay_ms(50)
                continue
            asrflag = 1
            break
        print("RunASR");
        return asrflag

    # /********************************************************************************
    # function:
                    # Hardware init
    # ********************************************************************************/
    def LD_init(self):
        config.LD_reset()

    # /********************************************************************************
    # function:
                    # Interrupt signal processing(ASR and Audio Player)
    # ********************************************************************************/
    def ProcessInt(self, fp):
        global nLD_Mode
        global nAsrStatus
        global nMp3Pos
        global nMp3Size
        global bMp3Play
        nAsrResCount = 0
        ucRegVal = config.LD_ReadReg(0x2B)
        ucHighInt = config.LD_ReadReg(0x29)         # interrupt enable flag
        ucLowInt = config.LD_ReadReg(0x02)          # interrupt enable flag
        config.LD_WriteReg(0x29, 0)                 # interrupt disenable
        config.LD_WriteReg(0x02, 0)                 # interrupt disenable
        if(nLD_Mode == LD_MODE_ASR_RUN): 
            print("---------------ASR---------------")
            #The interruption caused by speech recognition
            #(There is sound input, and there is interruption whether the recognition is successful or failed)
            if((ucRegVal & 0x10) and config.LD_ReadReg(0xb2)==0x21 and config.LD_ReadReg(0xbf)==0x35):
                nAsrResCount = config.LD_ReadReg(0xba)
                if(nAsrResCount>0 and nAsrResCount<=4):
                    print("ASR SUCCESSFUL ")
                    nAsrStatus = LD_ASR_FOUNDOK
                else:
                    print("ASR UNSUCCESSFUL ")
                    nAsrStatus = LD_ASR_FOUNDZERO
            else: 
                print("No ASR ")
                nAsrStatus = LD_ASR_FOUNDZERO
            config.LD_WriteReg(0x2b, 0)
            config.LD_WriteReg(0x1c, 0)
            return
        if(nLD_Mode == LD_MODE_MP3):
            print("--------------PLAY MP3--------------")
            # Play MP3 to produce 3 kinkd of intterupt
            # A. play over
            # B. data send over
            # C. Data will be used up and sent
            if(config.LD_ReadReg(0xBA) & CAUSE_MP3_SONG_END): 
                # A. play over
                config.LD_WriteReg(0x2B, 0)
                config.LD_WriteReg(0xBA, 0)	
                config.LD_WriteReg(0xBC, 0)	
                config.LD_WriteReg(0x08, 1)
                config.LD_WriteReg(0x08, 0)
                config.LD_WriteReg(0x33, 0)
                print("play over ")
                bMp3Play = 0                    # play status
                fp.close()
                # print(bMp3Play)
                return
            if(nMp3Pos >= nMp3Size): 
                # B. data send over
                config.LD_WriteReg(0xBC, 0x01)  #data voer
                config.LD_WriteReg(0x29, 0x10)
                print("data over ")
                return
            # C. Data will be used up and sent
            self.LD_ReloadMp3Data(fp)
            config.LD_WriteReg(0x29, ucHighInt)
            config.LD_WriteReg(0x02, ucLowInt)

    # /********************************************************************************
    # function:
                    # Start play
    # ********************************************************************************/
    def LD_play(self, fp, Mp3Size):
        global nMp3Pos
        global nMp3Size
        global bMp3Play
        
        bMp3Play = 1
        nMp3Pos = 0
        nMp3Size = Mp3Size
        
        # print(nMp3Size)
        if(nMp3Pos >=  nMp3Size):
            return
            
        self.LD_ReloadMp3Data(fp)
        config.LD_WriteReg(0xBA, 0x00)
        config.LD_WriteReg(0x17, 0x48)   #activate DSP
        config.LD_WriteReg(0x33, 0x01)   #play mp3
        config.LD_WriteReg(0x29, 0x04)   #FIFO interrupt allowed
        config.LD_WriteReg(0x02, 0x01)   #FIFO_DATA interrupt allowed 
        config.LD_WriteReg(0x85, 0x5A)

    # /********************************************************************************
    # function:
                    # Reload mp3 data
    # ********************************************************************************/
    def LD_ReloadMp3Data(self, fp):
        global nMp3Pos
        global nMp3Size
        # print("LD_ReloadMp3Data")
        # print(fp)
        ucStatus = config.LD_ReadReg(0x06)
        while (not(ucStatus&MASK_FIFO_STATUS_AFULL) and (nMp3Pos<nMp3Size)):
            val = fp.read(1)        #get 1 char data
            val = ord(val)          #char to hex
            nMp3Pos += 1
            # print(nMp3Pos)
            config.LD_WriteReg(0x01, val)
            ucStatus = config.LD_ReadReg(0x06)
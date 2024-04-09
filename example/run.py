import time
import multiprocessing
import os

#  根据需要填写需要运行的命令
def frpc():
    os.system('python3 ./stream_usb.py')

def httpServer():
    os.system('python3 ./mai.py')
 
def face2rmtp():
    os.system('python3 ./30_barometer.py')


if __name__ == '__main__':
    try:
        while 1:
            start = time.time()
            p1 = multiprocessing.Process(target=frpc,)
            p2 = multiprocessing.Process(target=httpServer,)
            p3 = multiprocessing.Process(target=face2rmtp,)
 
            # 启动子进程
            p1.start()
            p2.start()
            p3.start()
 
            # 等待fork的子进程终止再继续往下执行，可选填一个timeout参数
            p1.join()
            p2.join()
            p3.join()
    except KeyboardInterrupt:
        mi48.stop()
        cv.destroyAllWindows()
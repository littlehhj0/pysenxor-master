import cv2
# from ZNKJdigit import DigitalRecognizer,RecogniztionResult
cap=cv2.VideoCapture(0)
# 如果笔记本有前置和后置两个摄像头，一般0是后置，1是前置
# 每额外插一个usb摄像头，序号就会加1，多试试，就知道是几了。
cap.set(3,900)
cap.set(4,900)
# cap.set（）设置摄像头参数：3:宽   4:高
# cap.isOpened()返回布尔值，来查看是否摄像头初始化成功
while(cap.isOpened()):
    ret,frame = cap.read()
    # cap.read()返回两个值，第一个值为布尔值，如果视频正确，那么就返回true,  第二个值代表图像三维像素矩阵
    cv2.imshow('Capture', frame)
    # 保持画面的持续显示
    k=cv2.waitKey(1)
    # 等待1毫秒，没有继续刷新 如果是0 则是无限等待 cv2.waitKey(0)一般用于销魂窗口
    if k==ord('s'):
        print('222222')
        print(cap.get(3))
        print(cap.get(4))
    elif k==ord('q'):
        print('完成')
        cap.release()
        # 释放资源
        cv2.destroyAllWindows()
        # 删除窗口 注意英文单词 是destroy 不是destory
        break
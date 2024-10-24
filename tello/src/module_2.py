from djitellopy import Tello
import cv2
import numpy as np
import time
from time import sleep
import threading

def fly(tello: Tello):
    
    tello.move_up(100)

    tello.move_forward(80)

    # 修改这里
    # while True:
        # height = tello.get_height()
        # if height <= 40:
            # break
        # tello.move_down(20)  # 每次下降10厘米
        # sleep(0.1)  # 短暂暂停以允许高度更新

    tello.move_down(100)

    tello.move_left(40)

    tello.go_xyz_speed(80,-40,0,30)

    sleep(3)

    #tello.move_forward(80)

    #tello.move_right(40)

    # 修改这里
    # while True:
        # height = tello.get_height()
        # if height >= 100:  # 100厘米 = 1米
            # break
        # tello.move_up(20)  # 每次上升20厘米
        # sleep(0.1)  # 短暂暂停以允许高度更新

    tello.move_up(100)

    tello.move_forward(100)



def record_video(tello, video_writer):
    frame_time = 1 / 30  # 每帧的时间间隔（30 FPS）
    last_frame_time = time.time()
    while True:
        current_time = time.time()
        if current_time - last_frame_time >= frame_time:
            frame = tello.get_frame_read().frame
            frame = cv2.resize(frame, (960, 720))
            video_writer.write(frame)
            last_frame_time = current_time
        
        if should_exit:
            break

# 在 main 函数中添加一个全局变量来控制视频录制
def main():
    global should_exit
    should_exit = False
    
    tello = Tello()
    tello.connect()
    tello.takeoff()

    # 打开视频流
    tello.streamon()

    # 创建视频写入对象
    video_writer = cv2.VideoWriter('tello_flight.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30, (960, 720))

    # 创建并启动视频录制线程
    video_thread = threading.Thread(target=record_video, args=(tello, video_writer))
    video_thread.start()

    # 执行飞行
    fly(tello)

    # 设置退出标志
    should_exit = True

    # 等待视频录制线程结束
    video_thread.join()

    # 清理资源
    video_writer.release()
    cv2.destroyAllWindows()
    tello.streamoff()
    tello.land()

if __name__ == '__main__':
    main()

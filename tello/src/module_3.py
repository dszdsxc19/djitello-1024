from djitellopy import Tello
import cv2
import numpy as np
import time
from time import sleep
import threading

def main():
    tello = Tello()
    tello.connect()
    tello.takeoff()

    tello.move_forward(30)

    # 以50度角向前上方飞行
    distance = 120  # 飞行距离(厘米)``
    x = int(distance * np.cos(np.radians(50)))  # 水平距离
    z = int(distance * np.sin(np.radians(50)))  # 垂直距离
    tello.go_xyz_speed(x, 0, z, 50)  # x:前进, y:左右, z:上下, speed:速度

    # 等待第一段飞行完成
    tello.send_rc_control(0, 0, 0, 0)
    sleep(2)

    # 往前下方飞行，距离250厘米
    distance = 200  # 新的飞行距离(厘米)
    angle = -50  # 向下的角度，可以根据需要调整
    x = int(distance * np.cos(np.radians(angle)))  # 水平距离
    z = int(distance * np.sin(np.radians(angle)))  # 垂直距离（负值表示向下）
    tello.go_xyz_speed(x, 0, z, 50)  # x:前进, y:左右, z:上下, speed:速度

    tello.land()

if __name__ == "__main__":
    main()
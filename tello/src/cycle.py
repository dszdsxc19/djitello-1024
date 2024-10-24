import time

from djitellopy import Tello
import cv2
import numpy as np
import math, time

from src.tello import frame


def detect_move_cycle(tello, frame):
    # 创建HSV色彩空间中圆形的HSV阈值范围
    lower_blue = np.array([110, 50, 50])
    upper_blue = np.array([130, 255, 255])

    # 循环捕捉视频帧
    while True:
        # 获取新的视频帧
        frame = tello.get_frame_read().frame

        if frame is not None:
            # 将BGR视频帧转换为HSV色彩空间
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # 在HSV图像中提取圆形区域
            mask = cv2.inRange(hsv, lower_blue, upper_blue)
            # 对mask图像进行膨胀和腐蚀操作以去除噪声
            mask = cv2.dilate(mask, None, iterations=2)
            mask = cv2.erode(mask, None, iterations=2)

            # 寻找轮廓
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

            if len(cnts) > 0:
                # 找到最大的轮廓
                c = max(cnts, key=cv2.contourArea)
                # 计算轮廓的近似
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                center = (int(x), int(y))
                radius = int(radius)

                # 如果发现圆形，移动到圆心
                if radius > 10:
                    tello.send_rc_control(0, 0, 0, 0)
                    tello.move_to_xy(x, y)
                    break

            else:
                # 如果没有找到轮廓，向前飞行
                tello.send_rc_control(0, 0, 0, 30)

            # 在原始视频帧上绘制轮廓
            cv2.drawContours(frame, cnts, -1, (0, 255, 0), 2)

            # 显示视频帧
            cv2.imshow('Frame', frame)
            cv2.imshow('Mask', mask)


### detect line center ###
def find_green_pole(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 定义绿色的HSV范围
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([80, 255, 255])

    # 生成掩码（只保留绿色部分）
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # 使用形态学操作去除噪声
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # 找到轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        # 计算轮廓的边界框
        x, y, w, h = cv2.boundingRect(contour)

        # 找到中心点
        cx = x + w // 2
        cy = y + h // 2
        # 检查是否为竖直的杆（宽高比）
        aspect_ratio = w / h
        if 0.1 < aspect_ratio < 0.4:  # 这个比值需要根据实际情况调整

            # 在原图上绘制轮廓和中心点
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

            # 返回中心点和垂直方向（简单起见，我们假设竖直方向为(0, -1)即直向下）
            return cx, cy, (0, -1)
        if aspect_ratio > 2:
            return cx, cy, (-1, 0)
    return None, None, None

### fly a cycle start ###
def create_cycle_waypoints(center_x, certer_y, radius, num_points):
    waypoints = []
    for i in range(num_points):
        angle = (2*math.pi / num_points) * i
        x = center_x + radius*math.cos(angle)
        y = certer_y + radius*math.sin(angle)
        waypoints.append((x, y))
    return waypoints
def fly_to_waypoint(tello, x, y, z):
    tello.go_xyz_speed(x,y,z,20)
    time.sleep(2)

def fly_cycle(tello):
    frame = tello.get_frame_read().frame
    center_x, center_y, direction = find_green_pole(frame)
    certer_z = 50
    radius = 100
    num_points = 20

    waypoints = create_cycle_waypoints(center_x, center_y, radius, num_points)

    for x, y in waypoints:
        fly_to_waypoint(tello, x, y, certer_z)

### fly to a cycle center ###
def detect_circle(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5,5), 0)
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1.2, 100, param1=50, param2=30, minRadius=0, maxRadius=0)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            radius = i[2]
            cv2.circle(frame, center, radius, (0, 255, 0), 2)
            return center
    return None

def move_to_center(tello, center, frame_center):
    if center is not None:
        x_diff = center[0]-frame_center[0]
        y_diff = center[1]-frame_center[1]

        if abs(x_diff) > 20:
            if x_diff > 0:
                tello.move_right(abs(x_diff) // 2)
            else:
                tello.move_left(abs(x_diff) // 2)
        if abs(y_diff) > 20:
            if y_diff > 0:
                tello.move_down(abs(y_diff) // 2)
            else:
                tello.move_up(abs(y_diff) // 2)
def fly_to_center(tello):
    while True:
        frame = tello.get_frame_read().frame
        frame_center = (frame.shape[1] // 2, frame.shape[0] // 2)

        circle_center = detect_circle(frame)
        if circle_center is not None:
            tello.send_rc_control(0,0,0,0,0)
            move_to_center(tello, circle_center, frame_center)
        else:
            tello.send_rc_control(0, 0, 0, 0, 10)

        cv2.imshow("Tello", frame)

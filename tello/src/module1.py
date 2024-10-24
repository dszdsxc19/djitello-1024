import cv2
import numpy as np
from djitellopy import Tello
import time
import threading   
import math
from time import sleep

def detect_and_center_blue_pole(tello, duration=30, rotation_speed=20):
    """
    控制Tello无人机识别蓝色竖杆，将其居中，并返回距离和高度信息
    如果没有识别到或竖杆不符合条件则自转寻找
    
    参数:
    tello: Tello对象
    duration: 检测持续时间（秒），默认为60秒
    rotation_speed: 自转速度，默认为20
    
    返回:
    actual_distance: 到竖杆的实际距离（厘米）
    pole_height: 竖杆在图像中的高度（像素）
    """
    tello.streamon()
    
    start_time = time.time()
    rotating = False
    
    while time.time() - start_time < duration:
        frame = tello.get_frame_read().frame
        height, width = frame.shape[:2]
        
        # 转换到HSV颜色空间
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # 定义蓝色的HSV范围
        lower_blue = np.array([100, 50, 50])
        upper_blue = np.array([130, 255, 255])
        
        # 创建蓝色的掩码
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        
        # 对掩码进行形态学操作，去除噪点
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # 寻找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        pole_detected = False
        
        if contours:
            # 找到最大的轮廓
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # 检查竖杆高度是否大于屏幕高度的一定比例，且宽度相对较小
            if h > height * 0.95 and w < width * 0.4:
                print("Height", h, "Width", w)
                pole_detected = True
                rotating = False
                
                # 计算竖杆中心
                pole_center_x = x + w // 2
                pole_center_y = y + h // 2
                
                # 在图像上标记竖杆
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.circle(frame, (pole_center_x, pole_center_y), 5, (0, 0, 255), -1)
                
                # 获取TOF距离（厘米）
                distance = tello.get_distance_tof()
                
                # 计算竖杆到图像中心的水平偏移
                horizontal_offset = pole_center_x - width // 2
                
                # 如果竖杆在屏幕中央，返回距离和高度信息
                if abs(horizontal_offset) < width * 0.3:  # 允许10%的误差
                    # 计算实际距离（考虑水平角度）
                    fov = 82.6  # 假设水平FOV为82.6度
                    angle = horizontal_offset / (width/2) * (fov/2)
                    actual_distance = distance * np.cos(np.radians(angle))
                    
                    print(f"Blue pole centered. Distance: {actual_distance:.2f} cm, Height: {h} pixels")
                    tello.send_rc_control(0, 0, 0, 0)  # 停止移动
                    return actual_distance
                pole_detected = False
                
                print(f"Adjusting position.")
        
        if not pole_detected:
            # 如果没有检测到符合条件的蓝色竖杆，开始或继续旋转
            if not rotating:
                print("No suitable blue pole detected, starting rotation")
                rotating = True
            tello.send_rc_control(0, 0, 0, rotation_speed)
        
        # 显示图像
        cv2.imshow("Tello View", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # 如果超时未检测到，停止移动和视频流
    tello.send_rc_control(0, 0, 0, 0)
    tello.streamoff()
    cv2.destroyAllWindows()
    return None

def detect_and_align_with_blue_bar(tello, duration=60, rotation_speed=20):
    """
    控制Tello无人机识别前方最长的蓝色横杆，调整到相同高度，并测量距离
    如果没有识别到或横杆不够长则自转寻找
    同时显示摄像头画面
    
    参数:
    tello: Tello对象
    duration: 检测持续时间（秒），默认为60秒
    rotation_speed: 自转速度，默认为20
    """
    tello.streamon()
    
    start_time = time.time()
    rotating = False
    
    while time.time() - start_time < duration:
        frame = tello.get_frame_read().frame
        height, width = frame.shape[:2]
        
        # 转换到HSV颜色空间
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # 定义蓝色的HSV范围
        lower_blue = np.array([100, 50, 50])
        upper_blue = np.array([130, 255, 255])
        
        # 创建蓝色的掩码
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        
        # 对掩码进行形态学操作，去除噪点
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # 寻找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        bar_detected = False
        
        if contours:
            # 找到最长的横杆（宽度最大的轮廓）
            longest_bar = max(contours, key=lambda c: cv2.boundingRect(c)[2])
            x, y, w, h = cv2.boundingRect(longest_bar)
            print("w", w, "height", height)
            # 检查横杆长度是否大于屏幕宽度的一定比例，且高度相对较小
            if w > width * 0.95 and h < height * 0.1:
                bar_detected = True
                rotating = False
                
                # 在图像上标记横杆
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.circle(frame, (x+w//2, y+h//2), 5, (0, 0, 255), -1)
                
                # 获取TOF距离（厘米）
                distance = tello.get_distance_tof()
                
                # 计算横杆中心到图像中心的垂直偏移
                bar_center_y = y + h // 2
                vertical_offset = bar_center_y - height // 2
                
                # 调整无人机高度
                if abs(vertical_offset) > 20:  # 设置一个阈值，避免小幅度调整
                    up_down_velocity = int(vertical_offset * 0.2)  # 可以调整这个系数
                    tello.send_rc_control(0, 0, -up_down_velocity, 0)  # 注意y轴是反的
                else:
                    tello.send_rc_control(0, 0, 0, 0)
                
                # 在图像上显示距离信息
                cv2.putText(frame, f"Distance: {distance:.2f} cm", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                print(f"Detected blue bar at distance: {distance:.2f} cm, adjusting height")
        
        if not bar_detected:
            # 如果没有检测到足够长的蓝色横杆，开始或继续旋转
            if not rotating:
                print("No blue bar detected, starting rotation")
                rotating = True
            tello.send_rc_control(0, 0, 0, rotation_speed)
        
        # 显示图像
        cv2.imshow("Tello View", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # 停止移动和视频流
    tello.send_rc_control(0, 0, 0, 0)
    tello.streamoff()
    cv2.destroyAllWindows()

def fly_forward_circle(tello, radius, speed=30, clockwise=True):
    """
    控制Tello无人机以当前位置为起点，向前画一个圆
    
    参数:
    tello: Tello对象
    radius: 圆的半径（厘米）
    speed: 飞行速度（厘米/秒），默认为30
    clockwise: 是否顺时针飞行，默认为True
    """
    # 圆周长
    circumference = 2 * math.pi * radius
    
    # 估算完成一圈需要的时间（秒）
    flight_time = circumference / speed
    
    # 将圆分成多个小段
    segments = 36  # 可以根据需要调整，段数越多越平滑
    segment_time = flight_time / segments
    
    print(f"Flying a circle with radius {radius}cm at speed {speed}cm/s")
    print(f"Estimated flight time: {flight_time:.2f} seconds")
    
    for i in range(segments):
        # 计算当前段的角度（弧度）
        angle = 2 * math.pi * i / segments
        if not clockwise:
            angle = -angle
        
        # 计算x和y方向的速度
        vx = int(speed * math.cos(angle))
        vy = int(speed * math.sin(angle))
        
        # 发送控制命令
        tello.send_rc_control(vy, vx, 0, 0)
        
        # 等待这一小段完成
        time.sleep(segment_time)
    
    # 停止移动
    tello.send_rc_control(0, 0, 0, 0)

tello = Tello()

tello.connect()
print(tello.get_battery())

# 起飞
tello.takeoff()
print(tello.get_height())

## Step1: 穿越圈 ##
# tello.move_up(60)

# tello.move_right(100)
# #
# tello.move_forward(100)

# tello.move_down(60)

# fly_forward_circle(tello, 50, 20, True)

#### x:大于0前进， y:大于0左移， z:大于0上升

## Step2 Cycle: 水平绕杆一周半 ##
min_dis = 50
radius = min_dis
actual_distance = detect_and_center_blue_pole(tello, 30, 20)
if actual_distance > 0: 
    radius = int(actual_distance)
    # tello.go_xyz_speed(radius-50, 0, 0, 10)
    # radius = 50
    if radius > 70:
        tello.move_forward(radius-min_dis)
        radius = min_dis
    if radius < 30:
        tello.move_back(min_dis-radius)
        radius = min_dis
radius = radius -10
cos = int(0.5*radius)
sin = int(0.86*radius)
h = 0
speed = 20
tello.go_xyz_speed(cos, -sin, h, speed)
tello.go_xyz_speed(radius, 0, h, speed)
tello.go_xyz_speed(cos, sin, h, speed)

tello.go_xyz_speed(-cos, sin, h, speed)
tello.go_xyz_speed(-radius, 0, h, speed)
tello.go_xyz_speed(-cos, -sin, h, speed)

tello.go_xyz_speed(cos, -sin, h, speed)
tello.go_xyz_speed(radius, 0, h, speed)
tello.go_xyz_speed(cos, sin, h, speed)

tello.move_up(30)

# # ## Step3 Cycle: 垂直绕杆一周半 ##
v_radius = 50
v_min_dis = 50
bar_distance = detect_and_align_with_blue_bar(tello, 30, 20)
if bar_distance > 0: 
    v_radius = int(bar_distance)
    # tello.go_xyz_speed(radius-50, 0, 0, 10)
    # radius = 50
    if v_radius > 70:
        tello.move_forward(v_radius-v_min_dis)
        v_radius = v_min_dis
    if v_radius < 30:
        tello.move_back(v_min_dis-v_radius)
        v_radius = v_min_dis
v_radius = v_radius -10
v_cos = int(0.5*v_radius)
v_sin = int(0.86*v_radius)
h = 0
speed = 20
tello.go_xyz_speed(v_sin, 0, -v_cos, speed)
tello.go_xyz_speed(radius, 0, 0, speed)
tello.go_xyz_speed(v_sin, 0, v_cos, speed)

tello.go_xyz_speed(-v_sin, 0, v_cos, speed)
tello.go_xyz_speed(-radius, 0, 0, speed)
tello.go_xyz_speed(-v_sin, 0, -v_cos, speed)

tello.land()


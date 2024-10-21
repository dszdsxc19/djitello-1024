import cv2
import numpy as np
from djitellopy import Tello

def detect_circle(frame):
    # 转换为灰度图像
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # 高斯模糊
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # 霍夫圆变换
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, 100,
                               param1=100, param2=30, minRadius=50, maxRadius=200)
    
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            # 绘制圆形
            cv2.circle(frame, (i[0], i[1]), i[2], (0, 255, 0), 2)
            # 绘制圆心
            cv2.circle(frame, (i[0], i[1]), 2, (0, 0, 255), 3)
        return frame, circles[0, 0]
    return frame, None

def control_drone(drone, circle):
    if circle is None:
        return
    
    center_x, center_y, radius = circle
    frame_center_x, frame_center_y = 480, 360  # 假设帧大小为 960x720
    
    # 计算圆心与帧中心的偏差
    error_x = center_x - frame_center_x
    error_y = frame_center_y - center_y
    
    # 根据偏差调整无人机位置
    if abs(error_x) > 30:
        drone.left() if error_x < 0 else drone.right()
    if abs(error_y) > 30:
        drone.up() if error_y < 0 else drone.down()
    
    # 如果圆环足够大,认为已经接近,向前飞行
    if radius > 150:
        drone.move_forward(30)

# 初始化 Tello 无人机
drone = Tello()
drone.connect()
drone.takeoff()

# 开启视频流
drone.streamon()

while True:
    # 获取当前帧
    frame = drone.get_frame_read().frame
    
    # 检测圆环
    frame, circle = detect_circle(frame)
    
    # 控制无人机
    control_drone(drone, circle)
    
    # 显示帧
    cv2.imshow("Tello", frame)
    
    # 按 'q' 键退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 降落无人机
drone.land()

# 关闭视频流
drone.streamoff()

# 关闭所有窗口
cv2.destroyAllWindows()
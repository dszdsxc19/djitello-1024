import cv2
import numpy as np
from djitellopy import Tello

# 初始化Tello
tello = Tello()
tello.connect()

# 打开摄像头
cap = cv2.VideoCapture(0)

# 定义手势识别函数
def detect_gesture(frame):
    # 转换为HSV颜色空间
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # 定义肤色范围
    lower_skin = np.array([0, 20, 70], dtype=np.uint8)
    upper_skin = np.array([20, 255, 255], dtype=np.uint8)
    
    # 创建掩码
    mask = cv2.inRange(hsv, lower_skin, upper_skin)
    
    # 寻找轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # 获取最大轮廓
        max_contour = max(contours, key=cv2.contourArea)
        
        # 计算凸包
        hull = cv2.convexHull(max_contour, returnPoints=False)
        defects = cv2.convexityDefects(max_contour, hull)
        
        # 计算凸缺陷数量
        defect_count = 0
        for i in range(defects.shape[0]):
            s, e, f, d = defects[i, 0]
            if d > 20000:  # 设置阈值
                defect_count += 1
        
        # 根据凸缺陷数量判断手势
        if defect_count == 0:
            return "拳头"
        elif defect_count == 1:
            return "一根手指"
        elif defect_count == 4:
            return "手掌"
    
    return "未识别"
# 主循环
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    gesture = detect_gesture(frame)
    cv2.putText(frame, f"手势: {gesture}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imshow("Tello 手势控制", frame)
    
    # 根据手势控制Tello
    if gesture == "拳头":
        tello.land()
    elif gesture == "一根手指":
        tello.takeoff()
    elif gesture == "手掌":
        tello.move_up(30)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()
tello.land()
tello.end()

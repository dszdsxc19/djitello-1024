import cv2
import mediapipe as mp
import numpy as np
from djitellopy import Tello

def get_gesture(hand_landmarks):
    # 获取指尖和掌根的坐标
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

    # 计算每个指尖与手腕的距离
    fingers_up = [
        thumb_tip.y < wrist.y,
        index_tip.y < wrist.y,
        middle_tip.y < wrist.y,
        ring_tip.y < wrist.y,
        pinky_tip.y < wrist.y
    ]

    # 根据竖起的手指数量判断手势
    if sum(fingers_up) == 0:
        return "拳头"
    elif sum(fingers_up) == 1 and fingers_up[1]:
        return "一根手指"
    elif sum(fingers_up) == 5:
        return "手掌"
    else:
        return "未识别"

def control_drone(gesture):
    if gesture == "拳头":
        tello.land()
    elif gesture == "一根手指":
        tello.takeoff()
    elif gesture == "手掌":
        tello.move_up(30)
    else:
        tello.hover()


# 初始化Tello无人机
tello = Tello()
tello.connect()
tello.streamon()

# 初始化MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils


# 主循环
while True:
    frame = tello.get_frame_read().frame
    if frame is None:
        continue

    # 将图像转换为RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    gesture = "未识别"

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # 绘制手部关键点
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # 识别手势
            gesture = get_gesture(hand_landmarks)

            # 控制无人机
            control_drone(gesture)

    # 在屏幕上显示识别到的手势
    cv2.putText(frame, f"手势: {gesture}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Tello 手势控制", frame)

    # 按 'q' 键退出循环
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 结束程序
tello.land()
tello.streamoff()
cv2.destroyAllWindows()

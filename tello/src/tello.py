from time import sleep

from djitellopy import Tello
import cycle
### Parameters ###

fspeed = 117/10 # Forward speed in cm/s
aspeed = 360/10 # Speed Degrees/s
interval = 0.25

dInterval = fspeed*interval
aInterval = aspeed*interval

tello = Tello()

tello.connect()
print(tello.get_battery())

# 开启视频流
frame = tello.get_frame_read()

# tello.takeoff()
#
# print(tello.get_height())
#
# # tello.move_right(100)
# # tello.move_right(100)
# # tello.rotate_counter_clockwise(90)
# # tello.move_forward(100)
#
tello.move_up(50)

tello.move_right(130)

tello.move_forward(150)

cycle.detect_move_cycle(tello, frame)

sleep(5)

# # Step 2
# tello.rotate_counter_clockwise(-90)
# # sleep(2)
# tello.send_rc_control(0,30,0,-45)
# print(tello.get_height())
# sleep(9)
# tello.send_rc_control(0,0,0,0)
# sleep(3)
# tello.send_rc_control(0,30,0,-45)
# print(tello.get_height())
# sleep(8)
# tello.send_rc_control(0,0,0,0)
# sleep(2)
# tello.land()
#
# ##  Step 2
# tello.send_rc_control(0,30,30,0)
# sleep(3)
# tello.send_rc_control(0,0,0,0)
# sleep(1)
# tello.send_rc_control(0,-20,30,0)
# sleep(3)
# tello.send_rc_control(0,0,0,0)
# sleep(1)
# tello.send_rc_control(0,-20,-30,0)
# sleep(3)
# tello.send_rc_control(0,0,0,0)
# sleep(1)
# tello.send_rc_control(0,30,-30,0)
# sleep(3)
# tello.send_rc_control(0,0,0,0)
# sleep(1)
# tello.land()
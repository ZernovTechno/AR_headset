import threading

import cv2
import numpy as np
from PIL import Image

import gui
import tracking_mp_opt
from device_config import camera_size, screen_size
from camera import Camera

camera_width, camera_height = camera_size
screen_width, screen_height = screen_size


hand_image = np.zeros([screen_width // 2, screen_height, 4], dtype=np.uint8)

actual_image = np.zeros([screen_width // 2, screen_height, 3], dtype=np.uint8)

gui_image = np.zeros([screen_width // 2, screen_height, 4], dtype=np.uint8)

# left_actual_image =
right_actual_image = np.zeros([screen_width // 2, screen_height, 3], dtype=np.uint8)

fingers = [0]


def gui_driver():
    global fingers
    global gui_image
    while True:
        gui_image = gui_machine.create_GUI(fingers)
        # cv2.imshow("Eye: GUI", gui_image)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #    exit(0)


# def video_writer():
#     while True:
#         working_with = Image.fromarray(cv2.cvtColor(left_actual_image, cv2.COLOR_RGB2BGR))
#         working_with.paste(gui_image, (0, 0), gui_image)
#         out.write(cv2.cvtColor(np.array(working_with), cv2.COLOR_BGR2RGB))

detector = tracking_mp_opt.controller()
eyes_class = Camera()
gui_machine = gui.gui_machine()
# out = cv2.VideoWriter('outpy.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 25, (1480, 1440))

processes = [
    ['re', eyes_class.right.job],
    ['le', eyes_class.left.job],
    ['camera', eyes_class.run],
    # ['gui', gui_driver],
    # ["video", video_writer]
]

for i, (name, proc) in enumerate(processes):
    process = threading.Thread(name=name, target=proc)
    process.start()
    processes[i].append(process)
input()
# gui_machine_process = processes[3][1]

# while True:
#     if not gui_machine_process .is_alive:
#         gui_machine_process.start()

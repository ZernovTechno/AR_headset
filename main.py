import threading
import time

import cv2
import numpy as np
from PIL import Image
from numba import njit, prange

import gui
import tracking_mp_opt
from device_config import camera_size, screen_size

camera_width, camera_height = camera_size
screen_width, screen_height = screen_size

imshow_delay = 10

hand_image = np.zeros([screen_width // 2, screen_height, 4], dtype=np.uint8)

actual_image = np.zeros([screen_width // 2, screen_height, 3], dtype=np.uint8)

gui_image = np.zeros([screen_width // 2, screen_height, 4], dtype=np.uint8)

left_actual_image = np.zeros([screen_width // 2, screen_height, 3], dtype=np.uint8)
right_actual_image = np.zeros([screen_width // 2, screen_height, 3], dtype=np.uint8)

fingers = [0]


@njit(parallel=True)
def overlay_images(background, overlay, x, y):
    y_end = y + overlay.shape[0]
    x_end = x + overlay.shape[1]

    for i in prange(overlay.shape[0]):
        for j in prange(overlay.shape[1]):
            if overlay[i, j, 3] != 0:  # Check if the alpha channel is not transparent
                if 0 <= y + i < background.shape[0] and 0 <= x + j < background.shape[1]:
                    alpha = overlay[i, j, 3] / 255.0
                    inv_alpha = 1.0 - alpha
                    for c in range(3):
                        background[y + i, x + j, c] = (alpha * overlay[i, j, c] +
                                                       inv_alpha * background[y + i, x + j, c])

    return background


def gui_driver():
    global fingers
    global gui_image
    while True:
        gui_image = gui_machine.create_GUI(fingers)
        # cv2.imshow("Eye: GUI", gui_image)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #    exit(0)


class Eye:
    prev_frame_time = 0
    new_frame_time = 0

    def put_frame(self, frame: np.ndarray):
        # if frame==None:
        #     cv2.putText(self.left_actual_image, "NO IMAGE", (350, 512), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 255), 3,
        #                  cv2.LINE_AA)
        # return
        working_with = frame.copy()
        # working_with = cv2.rotate(working_with, cv2.ROTATE_180)
        font = cv2.FONT_HERSHEY_SIMPLEX
        new_frame_time = time.time()
        fps = 1 / (new_frame_time - self.prev_frame_time)
        self.prev_frame_time = new_frame_time
        fps = int(fps)
        fps = str(fps)
        cv2.putText(working_with, fps, (7, 70), font, 3, (100, 255, 0), 3, cv2.LINE_AA)
        # working_with = cv2.cvtColor(working_with, cv2.COLOR_RGB2RGBA)
        # working_with = overlay_images(working_with, cv2.cvtColor(np.array(gui_image), cv2.COLOR_BGRA2RGBA), 0,0)
        # if len(fingers) > 0:
        #    hands = Image.fromarray(cv2.cvtColor(hands, cv2.COLOR_RGBA2BGRA))
        #    working_with.paste(hands, (minx, miny), hands)

        cv2.imshow("Eye: RIGHT", working_with)
        if cv2.waitKey(imshow_delay) & 0xFF == ord('q'):
            exit(0)


class Eyes:
    left: Eye
    right: Eye

    def __init__(self):
        self.left = Eye()
        self.right = Eye()

    def run(self):
        while True:
            success, actual_image = stream.read()
            if success:
                self.right.put_frame(cv2.resize(actual_image[:camera_height, 0:camera_width // 2],
                                                (screen_width // 2, screen_height)))
                self.left.put_frame(cv2.resize(actual_image[:camera_height, (camera_width // 2):camera_width],
                                                (screen_width // 2, screen_height)))
            else:
                pass
                # self.left.put_frame(None)
                # self.right.put_frame(None)
                # cv2.putText(self.left_actual_image, "NO IMAGE", (350, 512), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 255), 3,
                #             cv2.LINE_AA)
                # cv2.putText(self.right_actual_image, "NO IMAGE", (350, 512), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 255), 3,
                #             cv2.LINE_AA)

    def work_right(self):
        prev_frame_time = 0
        new_frame_time = 0
        while True:
            working_with = right_actual_image.copy()
            working_with = cv2.rotate(working_with, cv2.ROTATE_180)
            font = cv2.FONT_HERSHEY_SIMPLEX
            new_frame_time = time.time()
            fps = 1 / (new_frame_time - prev_frame_time)
            prev_frame_time = new_frame_time
            fps = int(fps)
            fps = str(fps)
            cv2.putText(working_with, fps, (7, 70), font, 3, (100, 255, 0), 3, cv2.LINE_AA)
            # working_with = cv2.cvtColor(working_with, cv2.COLOR_RGB2RGBA)
            # working_with = overlay_images(working_with, cv2.cvtColor(np.array(gui_image), cv2.COLOR_BGRA2RGBA), 0,0)
            # if len(fingers) > 0:
            #    hands = Image.fromarray(cv2.cvtColor(hands, cv2.COLOR_RGBA2BGRA))
            #    working_with.paste(hands, (minx, miny), hands)

            cv2.imshow("Eye: RIGHT", working_with)
            if cv2.waitKey(imshow_delay) & 0xFF == ord('q'):
                exit(0)

    def work_left(self):
        global gui_image
        global fingers
        prev_frame_time = 0
        new_frame_time = 0
        while True:
            working_with = left_actual_image.copy()
            working_with = cv2.rotate(working_with, cv2.ROTATE_180)
            hands, fingers, miny, minx, maxy, maxx, mask = detector.find_and_get_hands(working_with)
            font = cv2.FONT_HERSHEY_SIMPLEX
            new_frame_time = time.time()
            fps = 1 / (new_frame_time - prev_frame_time)
            prev_frame_time = new_frame_time
            fps = int(fps)
            fps = str(fps)
            cv2.putText(working_with, fps, (7, 70), font, 3, (100, 255, 0), 3, cv2.LINE_AA)
            # working_with = overlay_images(working_with, cv2.cvtColor(np.array(gui_image), cv2.COLOR_BGRA2RGBA), 0,0)
            if len(fingers) > 0:
                working_with = overlay_images(working_with, hands, minx, miny)

            cv2.imshow("Eye: LEFT", working_with)
            if cv2.waitKey(imshow_delay) & 0xFF == ord('q'):
                exit(0)


def video_writer():
    while True:
        working_with = Image.fromarray(cv2.cvtColor(left_actual_image, cv2.COLOR_RGB2BGR))
        working_with.paste(gui_image, (0, 0), gui_image)
        out.write(cv2.cvtColor(np.array(working_with), cv2.COLOR_BGR2RGB))


detector = tracking_mp_opt.controller()
eyes_class = Eyes()
gui_machine = gui.gui_machine()
# out = cv2.VideoWriter('outpy.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 25, (1480, 1440))

stream = cv2.VideoCapture(0, cv2.CAP_DSHOW)
stream.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)  # Ширина кадров в видеопотоке.
stream.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)  # Высота кадров в видеопотоке.

processes = [
    # ['re', eyes_class.work_right],
    # ['le', eyes_class.work_left],
    ['both', eyes_class.run],
    ['gui', gui_driver],
    # ["video", video_writer]
]

for i, (name, proc) in enumerate(processes):
    process = threading.Thread(name=name, target=proc)
    process.start()
    processes[i].append(process)
gui_machine_process = processes[1][1]

# while True:
#     if not gui_machine_process .is_alive:
#         gui_machine_process.start()

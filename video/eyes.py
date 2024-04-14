import time

import cv2
import numpy as np

from device_config import camera_size, screen_size, eye_size

camera_width, camera_height = camera_size
screen_width, screen_height = screen_size
eye_width, eye_height = eye_size

imshow_delay = 1
font = cv2.FONT_HERSHEY_SIMPLEX
center_offset = camera_width//100

class Eye:

    name: str

    def __init__(self, name, camera):
        self.name = name
        self.camera = camera

    def job(self):
        print(f"Eye job started: {self.name}")
        frame = np.zeros([eye_width, eye_height, 3], dtype=np.uint8)
        prev_frame_time = 0
        while True:
            if self.name == 'left':
                frame = cv2.resize(self.camera.frame[:camera_height, center_offset:camera_width // 2+center_offset], eye_size)
            else:
                try:
                    frame = cv2.resize(self.camera.frame[:camera_height, (camera_width // 2-center_offset): camera_width-center_offset], eye_size)
                except:
                    pass
            new_frame_time = time.time()
            if new_frame_time!=prev_frame_time:
                fps = 1 / (new_frame_time - prev_frame_time)
                prev_frame_time = new_frame_time
                fps = str(int(fps))
                # cv2.rectangle(self.frame, (7, 0), (7 + 300, 70), (0, 0, 0), -1)
                cv2.putText(frame, fps, (7, 70), font, 3, (100, 255, 0), 3, cv2.LINE_AA)

            self.frame = frame
            # cv2.imshow(self.name, frame)
            # if cv2.waitKey(imshow_delay) & 0xFF == ord('q'):
            #     exit(0)

            # cv2.putText(self.frame, fps, (7, 70), font, 3, (100, 255, 0), 3, cv2.LINE_AA)

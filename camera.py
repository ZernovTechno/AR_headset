import cv2
import numpy as np

from device_config import eye_size
from eyes import Eye, camera_height, camera_width


class Camera:
    left: Eye
    right: Eye

    def __init__(self):

        stream = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        stream.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)  # Ширина кадров в видеопотоке.
        stream.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)  # Высота кадров в видеопотоке.

        self.left = Eye('left')
        self.right = Eye('right')
        self.stream = stream

    def run(self):
        print("Camera job started")
        while True:
            success, actual_image = self.stream.read()
            # cv2.putText(self.right_actual_image, "NO IMAGE", (350, 512), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 255), 3,
            #             cv2.LINE_AA)
            if not success or not isinstance(actual_image, np.ndarray):
                continue
            left = cv2.resize(actual_image[:camera_height, 0:camera_width // 2], eye_size)
            right = cv2.resize(actual_image[:camera_height, (camera_width // 2):camera_width], eye_size)
            self.left.put_frame(left)
            self.right.put_frame(right)

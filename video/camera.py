import cv2
import numpy as np

from video.eyes import camera_height, camera_width


class Camera:
    frame: np.ndarray

    def __init__(self):
        stream = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        stream.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)  # Ширина кадров в видеопотоке.
        stream.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)  # Высота кадров в видеопотоке.

        self.stream = stream
        self.frame = np.zeros([camera_width, camera_height, 3], dtype=np.uint8)

    def run(self):
        print("Camera job started")
        while True:
            success, actual_image = self.stream.read()

            if not success or not isinstance(actual_image, np.ndarray):
                continue

            self.frame = actual_image

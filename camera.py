import cv2
import numpy as np

from eyes import Eye, camera_height, camera_width


class Camera:
    left: Eye
    right: Eye
    ready: bool
    frame: np.ndarray
    def __init__(self):
        self.ready = False
        stream = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        stream.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)  # Ширина кадров в видеопотоке.
        stream.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)  # Высота кадров в видеопотоке.

        self.left = Eye('left', self)
        self.right = Eye('right', self)
        self.stream = stream
        self.frame = np.zeros([camera_width, camera_height, 3], dtype=np.uint8)

    def run(self):
        print("Camera job started")
        while True:

            success, actual_image = self.stream.read()

            if not success or not isinstance(actual_image, np.ndarray):
                continue

            self.frame = actual_image
            self.ready = True


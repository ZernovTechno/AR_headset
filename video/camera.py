import cv2
import numpy as np

from device_config import camera_size, eye_shift

camera_width, camera_height = camera_size


camera_center = camera_width // 2


class Camera:
    """
    Camera view service
    """
    frame: np.ndarray

    def __init__(self):
        stream = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        stream.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)
        stream.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)

        self.stream = stream
        self.frame = np.zeros([camera_width, camera_height, 3], dtype=np.uint8)

    def run(self):
        print("Camera job started")
        while True:
            success, actual_image = self.stream.read()

            if not success or not isinstance(actual_image, np.ndarray):
                continue

            left_end = eye_shift
            right_end = -eye_shift

            actual_image = actual_image[:, left_end:right_end]
            self.frame = actual_image

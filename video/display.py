import cv2
import numpy as np
from numba import njit, prange

from device_config import camera_size, imshow_delay, screen_size
from gui.widget import Widget
from tracking_mp_opt import controller
from video.camera import Camera

camera_width, camera_height = camera_size

camera_center = camera_width // 2


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


class Display:
    detector: controller
    user_widgets: list[Widget]
    system_widgets: list[Widget]
    camera: Camera

    camera_frame: np.ndarray

    def __init__(self, camera: Camera, detector: controller):
        self.camera = camera
        self.detector = detector
        self.user_widgets = []
        self.system_widgets = []

    def compose_video(self):
        print('Display job started')
        while True:
            self.camera_frame = self.camera.frame

            for widget in self.user_widgets:
                overlay_images(self.camera_frame, widget.render(), 0, 0)

            for widget in self.system_widgets:
                overlay_images(self.camera_frame, widget.render(), 0, 0)

            eye_width = camera_width//2

            left = self.camera_frame[:, :eye_width]
            right = self.camera_frame[:, -eye_width:]

            full_frame = np.concatenate((left, right), axis=1)

            final = cv2.resize(full_frame, screen_size)

            cv2.imshow("full", final)
            if cv2.waitKey(imshow_delay) & 0xFF == ord('q'):
                exit(0)

    def add_widget(self, widget: Widget):
        self.user_widgets.append(widget)

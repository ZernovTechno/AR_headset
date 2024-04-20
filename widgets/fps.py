import time

import cv2
import numpy as np

from gui.abstract.widget import Widget


class FPSCounter(Widget):
    prev_frame_time = 0
    font = cv2.FONT_HERSHEY_SIMPLEX

    counts = []

    def __init__(self):
        super().__init__()
        self.position = (7, 0)

    def render(self):
        frame = np.zeros((*self.screen_size, 4))

        cv2.rectangle(frame, (0, 0), (150, 70), (0, 0, 0, 255), -1)

        new_frame_time = time.time()
        if new_frame_time != self.prev_frame_time:
            self.counts.append(1 / (new_frame_time - self.prev_frame_time))
            self.prev_frame_time = new_frame_time

            if len(self.counts) > 50: self.counts.pop(0)
            fps = sum(self.counts) / len(self.counts)
            fps = str(int(fps))

            cv2.putText(frame, fps, (7, 70), self.font, 3, (100, 255, 0, 255), 3, cv2.LINE_AA)
        return frame

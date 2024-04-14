import cv2
import numpy as np
from numba import njit, prange

from video.eyes import Eye, imshow_delay


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
def compose_video(left:Eye, right:Eye):
    print('Display job started')
    while True:
        full_frame = np.concatenate((left.frame, right.frame), axis=1)
        cv2.imshow("full", full_frame)
        if cv2.waitKey(imshow_delay) & 0xFF == ord('q'):
            exit(0)
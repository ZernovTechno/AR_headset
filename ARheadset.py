import cv2
import threading
import numpy as np
import time
import tracking_mp_opt
import gui
from PIL import Image
from numba import njit, prange


hand_image = np.zeros([1480,1440,4],dtype=np.uint8)

actual_image = np.zeros([1480,1440,3],dtype=np.uint8)

gui_image = np.zeros([1440,1440,4],dtype=np.uint8)

left_actual_image = np.zeros([1480,1440,3],dtype=np.uint8)
right_actual_image = np.zeros([1480,1440,3],dtype=np.uint8)

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
        #cv2.imshow("Eye: GUI", gui_image)
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    exit(0)

class eyes():
    def __init__(self):
        pass

    def work_right(self):
        prev_frame_time = 0
        new_frame_time = 0
        while True:
            working_with = right_actual_image.copy()
            working_with = cv2.rotate(working_with,cv2.ROTATE_180)
            font = cv2.FONT_HERSHEY_SIMPLEX 
            new_frame_time = time.time() 
            fps = 1/(new_frame_time-prev_frame_time) 
            prev_frame_time = new_frame_time 
            fps = int(fps) 
            fps = str(fps) 
            cv2.putText(working_with, fps, (7, 70), font, 3, (100, 255, 0), 3, cv2.LINE_AA) 
            #working_with = cv2.cvtColor(working_with, cv2.COLOR_RGB2RGBA)
            #working_with = overlay_images(working_with, cv2.cvtColor(np.array(gui_image), cv2.COLOR_BGRA2RGBA), 0,0)
            #if len(fingers) > 0:
            #    hands = Image.fromarray(cv2.cvtColor(hands, cv2.COLOR_RGBA2BGRA))
            #    working_with.paste(hands, (minx, miny), hands)

            cv2.imshow("Eye: RIGHT", working_with)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                exit(0)

    def work_left(self):
        global gui_image
        global fingers
        prev_frame_time = 0
        new_frame_time = 0
        while True:
            working_with = left_actual_image.copy()
            working_with = cv2.rotate(working_with,cv2.ROTATE_180)
            hands, fingers, miny, minx, maxy, maxx, mask = detector.find_and_get_hands(working_with)
            font = cv2.FONT_HERSHEY_SIMPLEX 
            new_frame_time = time.time() 
            fps = 1/(new_frame_time-prev_frame_time) 
            prev_frame_time = new_frame_time 
            fps = int(fps) 
            fps = str(fps) 
            cv2.putText(working_with, fps, (7, 70), font, 3, (100, 255, 0), 3, cv2.LINE_AA) 
            #working_with = overlay_images(working_with, cv2.cvtColor(np.array(gui_image), cv2.COLOR_BGRA2RGBA), 0,0)
            if len(fingers) > 0:
                working_with = overlay_images(working_with, hands, minx, miny)

            cv2.imshow("Eye: LEFT", working_with)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                exit(0)
def video_writer():
    while True:
        working_with = Image.fromarray(cv2.cvtColor(left_actual_image, cv2.COLOR_RGB2BGR))
        working_with.paste(gui_image, (0, 0), gui_image)
        out.write(cv2.cvtColor(np.array(working_with), cv2.COLOR_BGR2RGB))

detector = tracking_mp_opt.controller()
eyes_class = eyes()
gui_machine = gui.gui_machine()
out = cv2.VideoWriter('outpy.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 25, (1480,1440))

if __name__ == '__main__': # Точка входа
    stream = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    stream.set(cv2.CAP_PROP_FRAME_WIDTH, 3840) # Ширина кадров в видеопотоке.
    stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080) # Высота кадров в видеопотоке.
    right_process = threading.Thread(name='right_eye', target=eyes_class.work_right) # Точка запуска потока правого глаза.
    left_process = threading.Thread(name='left_eye', target=eyes_class.work_left)
    gui_machine_process = threading.Thread(name='gui', target=gui_driver)
    videowriter = threading.Thread(name='video', target=video_writer)
    right_process.start()
    left_process.start()
    gui_machine_process.start()
    videowriter.start()
    while True:
        success, actual_image = stream.read()
        #right_actual_image = actual_image[:1080, 600:1770]
        #left_actual_image = actual_image[:1080, 1920+300:1920+1470]
        if (success):
            right_actual_image = cv2.resize(actual_image[:1080, 600:1920], (1480, 1440))
            left_actual_image= cv2.resize(actual_image[:1080, 2320:3840], (1480, 1440))
        else:
            cv2.putText(left_actual_image, "NO IMAGE", (350, 512), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 255), 3, cv2.LINE_AA)
            cv2.putText(right_actual_image, "NO IMAGE", (350, 512), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 255), 3, cv2.LINE_AA)
        if(not gui_machine_process.is_alive):
            gui_machine_process.start()

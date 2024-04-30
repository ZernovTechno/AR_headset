#######################################
#      C O N F I G U R A T I O N      #
#       К О Н Ф И Г У Р А Ц И Я       #
#######################################

#Set the type of camera(s)
#Установите тип камер

use_1_camera = True
use_1_cameras_width = 1280
use_1_cameras_height = 720

use_2_cameras = False
use_2_cameras_width = 1280
use_2_cameras_height = 720
use_2_cameras_first = 0
use_2_cameras_second = 1

use_PS5_camera = False # PS5 HD Camera. 1280x1080 by eye (Resize from 1920x1080). NEED DRIVER!!

use_PS4_camera = False # PS4 stereo camera. 1280x720 by eye. NEED DRIVER!!

#Choose a tracking module. The fastest now is "tracking_mp_opt"
#Выберите модуль трекинга. Самый быстрый на данный момент - "tracking_mp_opt"

import tracking_mp_opt as tracking #Fast
# import tracking_cvzone as tracking #Medium
# import tracking_v1 as tracking #Slow

#Run or not videorecorder?
#Запускать видеозапись или нет?
active_recording = True

#Turn the GUI on?
#Запускать GUI?
active_gui = True

#Turn webserver on?
#Запускать вебсервер?
active_flask = True


###################################################
#            M A I N   S O F T W A R E            #
#  П Р О Г Р А М М Н О Е   О Б Е С П Е Ч Е Н И Е  #
###################################################


import cv2
import threading
import numpy as np
import time
from PIL import Image
from numba import njit, prange

import gui as gui
from flask import Flask, render_template, Response
app = Flask(__name__)


actual_image = np.zeros([1480,1440,3],dtype=np.uint8)

gui_image = np.zeros([1440,1440,4],dtype=np.uint8)

left_actual_image = np.zeros([1480,1440,3],dtype=np.uint8)
right_actual_image = np.zeros([1480,1440,3],dtype=np.uint8)

left_postprocess_image = np.zeros([1480,1440,3],dtype=np.uint8)
right_postprocess_image = np.zeros([1480,1440,3],dtype=np.uint8) 


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
    print("Interface go, because stat: " + str(active_gui))
    while True:
        try:
            gui_image = gui_machine.create_GUI(fingers)
            #cv2.imshow("Eye: GUI", gui_image)
            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #    exit(0)
        except:
            print("GUI DRIVER FAILED!")
            pass
        
def gen_frames():  # generate frame by frame from camera
    global right_postprocess_image
    global left_postprocess_image
    while True:
        img1 = left_postprocess_image
        img2 = right_postprocess_image
        h1, w1 = img1.shape[:2]
        h2, w2 = img2.shape[:2]

        vis = np.zeros((max(h1, h2), w1+w2,3), np.uint8)

        vis[:h1, :w1,:3] = img1
        vis[:h2, w1:w1+w2,:3] = img2
        ret, buffer = cv2.imencode('.jpg', vis)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.route('/')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

hadanerror = False
error_string = "Nothing"
font = cv2.FONT_HERSHEY_SIMPLEX 
minx = 0
miny = 0
maxx = 0
maxy = 0

def work_right():
    global right_postprocess_image
    global minx
    global miny
    global maxx
    global maxy
    global fingers
    prev_frame_time = 0
    new_frame_time = 0
    while True:
        working_with = right_actual_image.copy()
        new_frame_time = time.time() 
        if len(fingers) > 0:
            hands, mask = detector.remove_background(working_with[miny:maxy, minx-200:maxx])
        fps = 1/(new_frame_time-prev_frame_time) 
        prev_frame_time = new_frame_time 
        fps = int(fps) 
        fps = str(fps) 
        cv2.putText(working_with, fps, (7, 70), font, 3, (100, 255, 0), 3, cv2.LINE_AA) 
        if active_gui: working_with = overlay_images(working_with, cv2.cvtColor(np.array(gui_image), cv2.COLOR_BGRA2RGBA), -200, 0)
        if len(fingers) > 0:
            working_with = overlay_images(working_with, hands, minx-200, miny)

        right_postprocess_image = working_with
        cv2.imshow("Eye: RIGHT", working_with)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            exit(0)

def work_left():
    global left_postprocess_image
    global fingers
    global minx
    global miny
    global maxx
    global maxy
    prev_frame_time = 0
    new_frame_time = 0
    while True:
        working_with = left_actual_image.copy()
        hands, fingers, miny, minx, maxy, maxx, mask = detector.find_and_get_hands(working_with)
        new_frame_time = time.time() 
        fps = 1/(new_frame_time-prev_frame_time) 
        prev_frame_time = new_frame_time 
        fps = int(fps) 
        fps = str(fps) 
        cv2.putText(working_with, fps, (7, 70), font, 3, (100, 255, 0), 3, cv2.LINE_AA) 
        if active_gui: working_with = overlay_images(working_with, cv2.cvtColor(np.array(gui_image), cv2.COLOR_BGRA2RGBA), 0,0)
        if len(fingers) > 0:
            working_with = overlay_images(working_with, hands, minx, miny)
 
        left_postprocess_image = working_with
        cv2.imshow("Eye: LEFT", working_with)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            exit(0)

def video_writer():
    print("Videowriter go, because stat: " + str(active_recording))
    while True:
        out.write(right_postprocess_image)

detector = tracking.controller()
gui_machine = gui.gui_machine()
out = cv2.VideoWriter("Recording_" + time.strftime("%d.%m.%Y_%H.%M.%S", time.localtime()) + ".avi",cv2.VideoWriter_fourcc(*"MJPG"), 25, (1480,1440))
                      
if __name__ == '__main__': # Точка входа
    if use_PS5_camera:
        stream = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        stream.set(cv2.CAP_PROP_FRAME_WIDTH, 3840) # Ширина кадров в видеопотоке.
        stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080) # Высота кадров в видеопотоке.

    elif use_2_cameras:
        stream = cv2.VideoCapture(use_2_cameras_first, cv2.CAP_DSHOW) # Левая камера
        stream.set(cv2.CAP_PROP_FRAME_WIDTH, use_2_cameras_width) # Ширина кадров в видеопотоке.
        stream.set(cv2.CAP_PROP_FRAME_HEIGHT, use_2_cameras_height) # Высота кадров в видеопотоке.
        stream1 = cv2.VideoCapture(use_2_cameras_second, cv2.CAP_DSHOW) # Правая камера
        stream1.set(cv2.CAP_PROP_FRAME_WIDTH, use_2_cameras_width) # Ширина кадров в видеопотоке.
        stream1.set(cv2.CAP_PROP_FRAME_HEIGHT, use_2_cameras_height) # Высота кадров в видеопотоке.

    elif use_1_camera:
        stream = cv2.VideoCapture(0, cv2.CAP_DSHOW) # Левая камера
        stream.set(cv2.CAP_PROP_FRAME_WIDTH, use_1_cameras_width) # Ширина кадров в видеопотоке.
        stream.set(cv2.CAP_PROP_FRAME_HEIGHT, use_1_cameras_height) # Высота кадров в видеопотоке.

    elif use_PS4_camera:
        stream = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        stream.set(cv2.CAP_PROP_FRAME_WIDTH, 2*1280) # Ширина кадров в видеопотоке.
        stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 800) # Высота кадров в видеопотоке.

    right_process = threading.Thread(name='right_eye', target=work_right).start() # Точка запуска потока правого глаза.
    left_process = threading.Thread(name='left_eye', target=work_left).start() # Точка запуска потока левого глаза.

    if active_recording:
        threading.Thread(name='video', target=video_writer).start()

    if active_gui:
        threading.Thread(name='gui', target=gui_driver).start()
    
    if active_flask:
        threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)).start()

    while True:
        if use_2_cameras:
            success, left_actual_image = stream.read()
            success, right_actual_image = stream1.read()
        else:
            success, actual_image = stream.read()
        actual_image = cv2.rotate(actual_image, cv2.ROTATE_180)

        if (success):
            if use_2_cameras:
                right_actual_image = cv2.resize(right_actual_image, (1480, 1440))
                left_actual_image= cv2.resize(left_actual_image, (1480, 1440))
            elif use_1_camera:
                right_actual_image = cv2.resize(actual_image, (1480, 1440))
                left_actual_image= cv2.resize(actual_image, (1480, 1440))
            else:
                right_actual_image = cv2.resize(actual_image[:actual_image.shape[0], actual_image.shape[1]//6:actual_image.shape[1]//2], (1480, 1440))
                left_actual_image= cv2.resize(actual_image[:actual_image.shape[0], actual_image.shape[1]//6*4:actual_image.shape[1]], (1480, 1440))
        else:
            cv2.putText(left_actual_image, "NO IMAGE", (350, 512), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 255), 3, cv2.LINE_AA)
            cv2.putText(right_actual_image, "NO IMAGE", (350, 512), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 255), 3, cv2.LINE_AA)

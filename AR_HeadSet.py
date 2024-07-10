###################################################
#            M A I N   S O F T W A R E            #
#  П Р О Г Р А М М Н О Е   О Б Е С П Е Ч Е Н И Е  #
###################################################

# 06.07.2024. Code version 5.
# Developed by Zernov.

import cv2
import threading
import numpy as np
import time
from PIL import Image
import io
import configparser
import gui as gui
from flask import Flask, render_template, Response
import tracking_mp_opt as tracking #Fast
import datetime

app = Flask(__name__)
config = configparser.ConfigParser()  # создаём объекта парсера

detector = tracking.controller()
gui_machine = gui.gui_machine() 

config.read("config.ini")  # читаем конфиг
if config["Options"]["barrel_distortion"] == "True":
    right_postprocess_image = np.zeros([1440,1440,3],dtype=np.uint8)
    left_postprocess_image = np.zeros([1440,1440,3],dtype=np.uint8)
    right_gui_image = np.zeros([1440,1440,3],dtype=np.uint8)
    left_gui_image = np.zeros([1440,1440,3],dtype=np.uint8)
else:
    right_postprocess_image = Image.new('RGB', (1440, 1440), (0,0,0))
    left_postprocess_image = Image.new('RGB', (1440, 1440), (0,0,0))
    right_gui_image = Image.new('RGBA', (1440, 1440), (0,0,0,0))
    left_gui_image = Image.new('RGBA', (1440, 1440), (0,0,0,0))
left_actual_image = np.zeros([1440,1440,3],dtype=np.uint8)
right_actual_image = np.zeros([1440,1440,3],dtype=np.uint8)
backgrnd = Image.new('RGB', (2960, 1440), (0,0,0))

font = cv2.FONT_HERSHEY_SIMPLEX 
minx = 0
miny = 0
maxx = 0
maxy = 0
fingers = []
xdegrees = 15
distance = 0

k_1 = 0.2
k_2 = 0.05
width = 1440
height = 1440
distCoeff = np.zeros((4,1),np.float64)
k1 = 5.0e-5
k2 = 0
p1 = 0
p2 = 0
distCoeff[0,0] = k1
distCoeff[1,0] = k2
distCoeff[2,0] = p1
distCoeff[3,0] = p2  
cam = np.eye(3,dtype=np.float32) 
cam[0,2] = width/2.0
cam[1,2] = height/2.0
cam[0,0] = 10.
cam[1,1] = 10.

timestamp = datetime.datetime.now().strftime("[%d-%m-%Y %H:%M:%S]")
logfilename = "logs/log_" + datetime.datetime.now().strftime("%d.%m.%Y_%H.%M") + ".txt"

TurnOff = False


def logger(text, mess_lvl = "Undefined"):
    timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    f = open(logfilename, 'a', encoding="utf-8")
    f.write('\n' + timestamp + " ["+ mess_lvl +"] " + text)
    f.close()

def gui_driver():
    global left_gui_image, right_gui_image, right_postprocess_image, xdegrees,fingers, miny, minx, maxy, maxx, distance
    logger("GUI запущен. Состояние из файла конфигурации: " + config["Options"]["active_interface"], "Debug")
    if config["Options"]["video_recording"]=="True":
        out = cv2.VideoWriter("saves/recording/recording_" + time.strftime("%d.%m.%Y_%H.%M.%S", time.localtime()) + ".avi", cv2.VideoWriter_fourcc(*'DIVX'), 15, (1440,1440))
    while True:
        if (TurnOff):
            out.release()
            exit()
        fingers, miny, minx, maxy, maxx, distance = detector.find_and_get_hands(left_actual_image)
        left_gui_image, right_gui_image = gui_machine.create_GUI(fingers, distance, xdegrees, config)
        if config["Options"]["video_recording"] == "True":
            out.write(right_postprocess_image)
        
def gen_frames():  # generate frame by frame from camera
    global right_postprocess_image
    global left_postprocess_image
    logger("Устройство просмотра подключено. Запуск трансляции через FLASK. Межзрачковое расстояние: "+ config["Customize"]["distance_between_eyes"] +" пикс.", "Debug")
    while True:
        if (TurnOff):
            exit()
        dbe = int(config["Customize"]["distance_between_eyes"])
        if config["Options"]["barrel_distortion"]=="True":
            backgrnd.paste(Image.fromarray(cv2.cvtColor(left_postprocess_image, cv2.COLOR_BGR2RGB)), (0 + abs(dbe-40), 0))
            backgrnd.paste(Image.fromarray(cv2.cvtColor(right_postprocess_image, cv2.COLOR_BGR2RGB)), (1440+ dbe, 0))
        else:
            backgrnd.paste(left_postprocess_image, (0 + abs(dbe-40), 0))
            backgrnd.paste(right_postprocess_image, (1440+ dbe, 0))
        img_byte_arr = io.BytesIO()
        backgrnd.save(img_byte_arr, format='jpeg')
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + img_byte_arr.getvalue() + b'\r\n')  # concat frame one by one and show result


@app.route('/')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def work_right():
    global right_postprocess_image
    logger("Правая камера запущена.", "Debug")
    while True:
        if (TurnOff):
            exit()
        if config["Options"]["barrel_distortion"] == "True":
            right_postprocess_image = cv2.undistort(cv2.addWeighted(right_gui_image, 0.6, right_actual_image, 0.6, 0),cam,distCoeff)
        else:
            working_with = Image.fromarray(cv2.cvtColor(right_actual_image, cv2.COLOR_BGR2RGB))
            working_with.paste(right_gui_image, (0,0), right_gui_image)
            right_postprocess_image = working_with

def work_left():
    global left_postprocess_image
    logger("Левая камера запущена.", "Debug")
    while True:
        if (TurnOff):
            exit()
        #left_postprocess_image = distort(np.where(left_gui_image[..., 2][..., None] > 0, left_gui_image, left_actual_image))
        if config["Options"]["barrel_distortion"] == "True":
            left_postprocess_image = cv2.undistort(cv2.addWeighted(left_gui_image, 0.6, left_actual_image, 0.6, 0),cam,distCoeff)
        else:
            working_with = Image.fromarray(cv2.cvtColor(left_actual_image, cv2.COLOR_BGR2RGB))
            working_with.paste(left_gui_image, (0,0), left_gui_image)
            left_postprocess_image = working_with

if __name__ == '__main__': # Точка входа
    logger("Точка входа.", "Debug")
    camera_mode = config["Camera"]["mode"]
    match camera_mode:
        case "ps5camera":
            logger("Выбрана PS5 камера.", "Debug")
            stream = cv2.VideoCapture(int(config["Camera"]["ps5camera_id"]), cv2.CAP_DSHOW)
            stream.set(cv2.CAP_PROP_FRAME_WIDTH, 3840) # Ширина кадров в видеопотоке.
            stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080) # Высота кадров в видеопотоке.

        case "2camera":
            logger("Выбран режим двух камер.", "Debug")
            stream = cv2.VideoCapture(int(config["Camera"]["first_camera_id"]), cv2.CAP_DSHOW) # Левая камера
            stream.set(cv2.CAP_PROP_FRAME_WIDTH, int(config["Camera"]["resolution_w"])) # Ширина кадров в видеопотоке.
            stream.set(cv2.CAP_PROP_FRAME_HEIGHT,int(config["Camera"]["resolution_h"])) # Высота кадров в видеопотоке.
            stream1 = cv2.VideoCapture(int(config["Camera"]["second_camera_id"]), cv2.CAP_DSHOW) # Правая камера
            stream1.set(cv2.CAP_PROP_FRAME_WIDTH, int(config["Camera"]["resolution_w"])) # Ширина кадров в видеопотоке.
            stream1.set(cv2.CAP_PROP_FRAME_HEIGHT, int(config["Camera"]["resolution_h"])) # Высота кадров в видеопотоке.

        case "1camera":
            logger("Выбран режим одной камеры.", "Debug")
            stream = cv2.VideoCapture(0, cv2.CAP_DSHOW) # Левая камера
            stream.set(cv2.CAP_PROP_FRAME_WIDTH, int(config["Camera"]["resolution_w"])) # Ширина кадров в видеопотоке.
            stream.set(cv2.CAP_PROP_FRAME_HEIGHT, int(config["Camera"]["resolution_h"])) # Высота кадров в видеопотоке.

        case "ps4camera":
            logger("Выбрана камера PS4.", "Debug")
            stream = cv2.VideoCapture(int(config["Camera"]["ps4camera_id"]), cv2.CAP_DSHOW)
            stream.set(cv2.CAP_PROP_FRAME_WIDTH, 2560) # Ширина кадров в видеопотоке.
            stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 800) # Высота кадров в видеопотоке.
            stream.set(cv2.CAP_PROP_FPS, 60) # Высота кадров в видеопотоке.
        case _:
            logger("Никакая камера не выбрана.", "Debug")
            stream = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if config["Options"]["active_interface"] == "True":
        logger("Попытка запуска потока интерфейса.", "Debug")
        threading.Thread(name='gui', target=gui_driver).start()
    
    if config["Options"]["webserver_active"] == "True":
        logger("Попытка запуска потока ВЕБ-сервера.", "Debug")
        threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)).start()

    threading.Thread(name='right_eye', target=work_right).start() # Точка запуска потока правого глаза.
    threading.Thread(name='left_eye', target=work_left).start() # Точка запуска потока левого глаза.
    #threading.Thread(name='driver', target=driver).start() # Точка запуска потока левого глаза.

    while True:
        if (TurnOff):
            exit()
        match camera_mode:
            case "2camera":
                success, left_actual_image = stream.read()
                success, right_actual_image = stream1.read()
            case _:
                success, actual_image = stream.read()
        if config["Camera"]["rotate_image"] == "True":
            actual_image = cv2.rotate(actual_image, cv2.ROTATE_180)
        if (success and config["Camera"]["mode"] != "camera_off"):
            match camera_mode:
                case "2camera":
                    right_actual_image = cv2.resize(right_actual_image, (1440, 1440))
                    left_actual_image= cv2.resize(left_actual_image, (1440, 1440))
                case "1camera":
                    right_actual_image = cv2.resize(actual_image[:actual_image.shape[0], actual_image.shape[1]//10*2:actual_image.shape[1]//10*8], (1440, 1440))
                    left_actual_image= cv2.resize(actual_image[:actual_image.shape[0], actual_image.shape[1]//10*1:actual_image.shape[1]//10*7], (1440, 1440))
                case _:
                    right_actual_image = cv2.resize(actual_image[:actual_image.shape[0], actual_image.shape[1]//6:actual_image.shape[1]//2], (1440, 1440))
                    left_actual_image= cv2.resize(actual_image[:actual_image.shape[0], actual_image.shape[1]//6*4-100:actual_image.shape[1]-100], (1440, 1440))
        else:
            cv2.putText(left_actual_image, "NO IMAGE", (350, 512), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 255), 3, cv2.LINE_AA)
            cv2.putText(right_actual_image, "NO IMAGE", (150, 512), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 255), 3, cv2.LINE_AA)

import cv2
import threading
import numpy as np
import time
from PIL import Image
# import io

import gui as gui
from flask import Flask, Response, render_template

#######################################
#      C O N F I G U R A T I O N      #
#       К О Н Ф И Г У Р А Ц И Я       #
#######################################

# Choose a tracking module. The fastest now is "tracking_mp_opt"
# Выберите модуль трекинга. Самый быстрый на данный момент - "tracking_mp_opt"

import tracking_mp_opt as tracking  # Fast

# import tracking_cvzone as tracking #Medium
# import tracking as tracking #Slow

# Set the type of camera(s)
# Установите тип камер

use_1_camera = True

use_2_cameras = False
use_2_cameras_first = 0
use_2_cameras_second = 1

use_PS5_camera = False  # PS5 HD Camera. 1280x1080 by eye (Resize from 1920x1080). NEED DRIVER!!

use_PS4_camera = False  # PS4 stereo camera. 1280x720 by eye. NEED DRIVER!!

camera_index = 0  # for (1 cam | ps5 | ps4) mode
rotate_180 = False
cameras_width = 1280
cameras_height = 720

# Run or not video-recorder?
# Запускать видеозапись или нет?
active_recording = False

# Turn the GUI on?
# Запускать GUI?
active_gui = True

# Turn webserver on?
# Запускать вебсервер?
active_flask = True

###################################################
#            M A I N   S O F T W A R E            #
#  П Р О Г Р А М М Н О Е   О Б Е С П Е Ч Е Н И Е  #
###################################################


app = Flask(__name__)

actual_image = np.zeros([1440, 1480, 3], dtype=np.uint8)

gui_image = Image.fromarray(np.zeros([1480, 1480, 4], dtype=np.uint8))

left_actual_image = np.zeros([1440, 1480, 3], dtype=np.uint8)
right_actual_image = np.zeros([1440, 1480, 3], dtype=np.uint8)

left_postprocess_image = np.zeros([1440, 1480, 3], dtype=np.uint8)
right_postprocess_image = np.zeros([1440, 1480, 3], dtype=np.uint8)

fingers = [0]


def gui_driver():
    global fingers
    global gui_image
    print("Interface go, because stat: " + str(active_gui))
    while True:
        # try:
        gui_image = Image.fromarray(cv2.cvtColor(np.array(gui_machine.create_gui(fingers)), cv2.COLOR_RGBA2BGRA))
        # gui_image = gui_machine.create_GUI(fingers)
        # cv2.imshow("Eye: GUI", gui_image)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #    exit(0)
        # except:
        #    cv2.putText(gui_image, "Gui Failed.", (350, 100), cv2.FONT_HERSHEY_SIMPLEX, 4,
        #    (0, 0, 255, 255), 3, cv2.LINE_AA)
        #    #pass


def gen_frames():  # generate frame by frame from camera
    global right_postprocess_image
    global left_postprocess_image
    # backgrnd = Image.new('RGB', (2960, 1440), (0, 0, 0))
    h, w, c = 1440, 1480, 3
    black_streak = np.zeros((h, int(w * 0.6), c), dtype=np.uint8)
    while True:
        # backgrnd.paste(left_postprocess_image, (0, 0), left_postprocess_image)
        # backgrnd.paste(right_postprocess_image, (1480, 0), right_postprocess_image)
        #
        # img_byte_arr = io.BytesIO()
        # frame = cv2.cvtColor(np.concatenate((left_postprocess_image, right_postprocess_image), axis=1)
        #                      , cv2.COLOR_RGB2BGR)
        # backgrnd.save(img_byte_arr, format='jpeg')
        # frame = img_byte_arr.getvalue()
        frame = np.concatenate((left_postprocess_image, black_streak, right_postprocess_image),
                               axis=1)
        img_byte_arr = cv2.imencode('.jpg', frame)[1].tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img_byte_arr + b'\r\n')  # concat frame one by one and show result


@app.route('/')
def index() -> str:
    return render_template('index.html')


@app.route('/script.js')
def script() -> str:
    return render_template('script.js')


@app.route('/video_feed')
def video_feed() -> Response:
    # Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


hadanerror = False
error_string = "Nothing"
font = cv2.FONT_HERSHEY_SIMPLEX
min_x = 0
min_y = 0
max_x = 0
max_y = 0

left = False
right = True


def work_right():
    global right_postprocess_image
    global min_x
    global min_y
    global max_x
    global max_y
    global left
    global right
    global fingers
    prev_frame_time = -1
    while True:
        working_with = right_actual_image.copy()
        new_frame_time = time.time()
        fps = int(1 // (new_frame_time - prev_frame_time))
        cv2.putText(working_with, str(fps), (7, 70), font, 3, (100, 255, 0), 3, cv2.LINE_AA)
        prev_frame_time = time.time()
        if len(fingers) > 0:
            hands, mask = detector.remove_background(working_with[min_y:max_y, min_x - 220:max_x])
            hands = Image.fromarray(hands)
            working_with = Image.fromarray(working_with)
            working_with.paste(hands, (min_x - 220, min_y), hands)
        else:
            working_with = Image.fromarray(working_with)
        if active_gui:
            working_with.paste(gui_image, (-200, 0), gui_image)
        if len(fingers) > 0:
            working_with.paste(hands, (min_x - 220, min_y), hands)
        # fps = int(fps)
        # fps = str(fps)
        # working_with = Image.fromarray(working_with)
        # if len(fingers) > 0:
        #     # try:
        #     # hands = Image.fromarray(cv2.cvtColor(hands, cv2.COLOR_BGRA2RGBA))
        #     # except:
        #     #     pass
        right_postprocess_image = np.asarray(working_with)


def work_left():
    global left_postprocess_image
    global fingers
    global min_x
    global min_y
    global max_x
    global max_y
    global left
    global right
    prev_frame_time = -1
    while True:
        working_with = left_actual_image.copy()
        hands, fingers, min_y, min_x, max_y, max_x, mask = detector.find_and_get_hands(working_with)
        new_frame_time = time.time()
        fps = int(1 // (new_frame_time - prev_frame_time))
        cv2.putText(working_with, str(fps), (7, 70), font, 3, (100, 255, 0), 3, cv2.LINE_AA)
        prev_frame_time = time.time()
        working_with = Image.fromarray(working_with)
        if active_gui:
            working_with.paste(gui_image, (0, 0), gui_image)
        if len(fingers) > 0:
            hands = Image.fromarray(hands)
            working_with.paste(hands, (min_x, min_y), hands)
        left_postprocess_image = np.asarray(working_with)


def video_writer():
    global right_postprocess_image
    print("Videowriter go, because stat: " + str(active_recording))
    out = cv2.VideoWriter("saves/recording/recording_" + time.strftime("%d.%m.%Y_%H:%M:%S", time.localtime()) + ".avi",
                          cv2.VideoWriter_fourcc(*"MJPG"), 25, (1480, 1440))
    while True:
        out.write(np.array(cv2.cvtColor(right_postprocess_image, cv2.COLOR_RGB2BGR)))


detector = tracking.controller()
gui_machine = gui.GUIMachine()

if __name__ == '__main__':  # Точка входа
    if use_PS5_camera:
        stream = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        stream.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)  # Ширина кадров в видеопотоке.
        stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)  # Высота кадров в видеопотоке.
    elif use_2_cameras:
        stream = cv2.VideoCapture(use_2_cameras_first, cv2.CAP_DSHOW)  # Левая камера
        stream.set(cv2.CAP_PROP_FRAME_WIDTH, cameras_width)  # Ширина кадров в видеопотоке.
        stream.set(cv2.CAP_PROP_FRAME_HEIGHT, cameras_height)  # Высота кадров в видеопотоке.
        stream1 = cv2.VideoCapture(use_2_cameras_second, cv2.CAP_DSHOW)  # Правая камера
        stream1.set(cv2.CAP_PROP_FRAME_WIDTH, cameras_width)  # Ширина кадров в видеопотоке.
        stream1.set(cv2.CAP_PROP_FRAME_HEIGHT, cameras_height)  # Высота кадров в видеопотоке.
    elif use_1_camera:
        stream = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)  # Левая камера
        stream.set(cv2.CAP_PROP_FRAME_WIDTH, cameras_width)  # Ширина кадров в видеопотоке.
        stream.set(cv2.CAP_PROP_FRAME_HEIGHT, cameras_height)  # Высота кадров в видеопотоке.
    elif use_PS4_camera:
        stream = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        stream.set(cv2.CAP_PROP_FRAME_WIDTH, 2 * 1280)  # Ширина кадров в видеопотоке.
        stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)  # Высота кадров в видеопотоке.
    else:
        print('camera no select :(')
        quit()

    right_thread = threading.Thread(name='right_eye', target=work_right, daemon=True)  # .start return None | bug fix
    right_thread.start()  # Точка запуска потока правого глаза.
    left_thread = threading.Thread(name='left_eye', target=work_left, daemon=True)
    left_thread.start()  # Точка запуска потока левого глаза.

    if active_recording:
        threading.Thread(name='video', target=video_writer, daemon=True).start()

    if active_gui:
        threading.Thread(name='gui', target=gui_driver, daemon=True).start()

    if active_flask:
        threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False),
                         daemon=True).start()

    while True:
        if use_2_cameras:
            success1, left_actual_image = stream.read()
            # noinspection PyUnboundLocalVariable
            success2, right_actual_image = stream1.read()
            success = success1 and success2  # bug fix
        else:
            success, actual_image = stream.read()

        if rotate_180:
            actual_image = cv2.rotate(actual_image, cv2.ROTATE_180)

        if success:
            if use_2_cameras:
                right_actual_image = cv2.resize(right_actual_image, (1480, 1440))
                left_actual_image = cv2.resize(left_actual_image, (1480, 1440))
            elif use_1_camera:
                right_actual_image = cv2.resize(actual_image, (1480, 1440))
                left_actual_image = cv2.resize(actual_image, (1480, 1440))
            else:
                right_actual_image = cv2.resize(
                    actual_image[:actual_image.shape[0], actual_image.shape[1] // 6:actual_image.shape[1] // 2],
                    (1480, 1440))
                left_actual_image = cv2.resize(
                    actual_image[:actual_image.shape[0], actual_image.shape[1] // 6 * 4:actual_image.shape[1]],
                    (1480, 1440))
        else:
            cv2.putText(left_actual_image, "can't get frame", (220, 512),
                        cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 0, 255), 3, cv2.LINE_AA)
            cv2.putText(right_actual_image, "can't get frame", (20, 512),
                        cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 0, 255), 3, cv2.LINE_AA)

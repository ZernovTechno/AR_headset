import cv2
import mediapipe as mp
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from cvzone.SelfiSegmentationModule import SelfiSegmentation
import multiprocessing
from multiprocessing import Process
from dataclasses import dataclass, field
import datetime
import time 

segmentor = SelfiSegmentation()

def check_in_region(top_left, bottom_right, point):
    if (point[2] > top_left[1]-20 and point[2] < bottom_right[1]+20 and point[1] > top_left[0]-20 and point[1] < bottom_right[0]+20): # Check if point coordinates inside the region
        return True
    else:
        return False

class handDetector():
    def __init__(self, mode=False, maxHands=2, modelComplex=1, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.modelComplex = modelComplex
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.modelComplex, self.detectionCon, self.trackCon)

        self.mpDraw = mp.solutions.drawing_utils
    def findHands(self, img, draw=False):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        #print(self.results.multi_hand_landmarks)
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
        return img
    def findPosition(self, img, handNo=0, draw=False):
        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                # print(id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                # print(id, cx, cy)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
        return lmList
    @staticmethod
    def remove_background(capture):
        result2 = segmentor.removeBG(capture, (0, 0, 0), 0.07)
        src = result2
        tmp = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        _,alpha = cv2.threshold(tmp,0,255,cv2.THRESH_BINARY)
        b, g, r = cv2.split(src)
        rgba = [b,g,r, alpha]
        dst = cv2.merge(rgba,4)
        return dst
    @staticmethod
    def remove_background_old(img): # Оптимизация (НЕ СРАБОТАЛО)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        ret, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_TRIANGLE) 
        mask = cv2.bitwise_not(mask)
        kernel = np.ones((9,9), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # put mask into alpha channel of result
        result = img.copy()
        result = cv2.cvtColor(result, cv2.COLOR_BGR2BGRA)
        result[:, :, 3] = mask
        cv2.imshow("hand", result)
        return result
    
    @staticmethod
    def find_and_get_hands(img):
        cropimgwithoutbg = img.copy()
        img_hands = img.copy()
        img_hands = detector.findHands(img_hands)
        fingers = detector.findPosition(img_hands)
        minx = 0
        miny = 0
        if (len(fingers) >= 20):
            xlist = [0]
            ylist = [0]

            for ids in fingers:
                xlist.append(ids[1])
                ylist.append(ids[2])

            minx = min(xlist) - 80
            maxx = max(xlist) + 80
            miny = min(ylist) - 80
            maxy = max(ylist) + 80
            if (minx <= 0): minx = 1
            if (maxx <= 0): maxx = 1
            if (maxy <= 0): maxy = 1
            if (miny <= 0): miny = 1

            cropimg = cropimgwithoutbg[miny:maxy, minx:maxx]
            cropimgwithoutbg = detector.remove_background(cropimg)    
            cropimgwithoutbg = Image.fromarray(cv2.cvtColor(cropimgwithoutbg, cv2.COLOR_BGRA2RGBA))
        return fingers, cropimgwithoutbg, minx, miny
detector = handDetector()

@dataclass
class GUI_object(): # Class interface object.
    """Тип данных объект интерфейса"""
    active: bool = None # Shows object on next draw
    size: int = field(default_factory=list) # Size of created GUI object
    destination: int = field(default_factory=list) # Destination of created GUI object
    def __post_init__(self): # Post init function. Creates border and background by size param
        # инициализация переменной `total`
        self.image = Image.new('RGBA', self.size, (255, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)

clocks = GUI_object(True, size=[200, 100], destination=[400, 100])

def create_GUI (fingers): # Make an interface overlay
    if (len(fingers) > 20):
        controller(fingers)

    gui = Image.new('RGBA', (1024, 1024), (0,0,0,0))

    if (clocks.active):
        clocks.__post_init__()
        now = datetime.datetime.now()
        time = now.strftime("%H:%M")
        data = now.strftime("%d-%m-%Y")
        clocks.draw.rounded_rectangle(((0, 0), clocks.size), 20, fill=(255,255,255, 230))
        clocks.draw.text(((clocks.size[0] // 3 -40), (clocks.size[1] // 3 -15)),data,(255,255,255),font=ImageFont.truetype("sans-serif.ttf", 30))
        clocks.draw.text(((clocks.size[0] // 2 -40), (clocks.size[1] // 3 +15)),time,(255,255,255),font=ImageFont.truetype("sans-serif.ttf", 30))
    
    gui.paste(clocks.image, clocks.destination, clocks.image)
    return gui

fingers_old = [0,0,0,0]

def controller(fingers): # Get fingers positions and check interface
    big_finger_coordinates = fingers[4] # Большой палец (координаты)
    index_finger_coordinates = fingers[8] # Указательный палец (координаты)
    middle_finger_coordinates = fingers[12] # Средний палец (координаты) 
    ring_finger_coordinates = fingers[16] # Безымянный палец (координаты)
    pinky_finger_coordinates = fingers[20] # Мизинец (координаты)

    if (abs(big_finger_coordinates[1] - index_finger_coordinates[1]) < 60 and abs(big_finger_coordinates[2] - index_finger_coordinates[2]) < 60): # Check, if index finger near the big finger
        # if index near big.
        if (check_in_region(clocks.destination, [clocks.destination[0] + clocks.size[0], clocks.destination[1] + clocks.size[1]], index_finger_coordinates)): # Check, if index finger inside the clocks
            clocks.destination = [index_finger_coordinates[1]-clocks.size[0]//2, index_finger_coordinates[2]-clocks.size[1]//2] # Set the center of clocks to the index finger
    fingers_old = fingers

def left_work(): # Do stuff, needed in left eye. Cuts and pastes hands, creates and overlays GUI.
    left_stream = cv2.VideoCapture(1)
    left_stream.set(cv2.CAP_PROP_FPS, 30) # Частота кадров
    left_stream.set(cv2.CAP_PROP_FRAME_WIDTH, 1920) # Ширина кадров в видеопотоке.
    left_stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080) # Высота кадров в видеопотоке.
    prev_frame_time = 0
    new_frame_time = 0
    while True:
        _, img = left_stream.read()
        img = img[0:1024, 600:1770]
        fingers, hands, minx_of_hands, miny_of_hands = detector.find_and_get_hands(img)
        gui_global = create_GUI(fingers)
        compressed_image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA))
        compressed_image.paste(gui_global, [0,0], gui_global)
        if (len(fingers) >= 20):
            compressed_image.paste(hands, [minx_of_hands, miny_of_hands], hands)

        cv2_compressed_image = cv2.cvtColor(np.array(compressed_image), cv2.COLOR_BGRA2RGBA)

        font = cv2.FONT_HERSHEY_SIMPLEX 
        new_frame_time = time.time() 
        fps = 1/(new_frame_time-prev_frame_time) 
        prev_frame_time = new_frame_time 
        fps = int(fps) 
        fps = str(fps) 
        cv2.putText(cv2_compressed_image, fps, (7, 70), font, 3, (100, 255, 0), 3, cv2.LINE_AA) 

        cv2.imshow("Left", cv2_compressed_image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            exit(0)

def right_work(): # Do stuff, needed in right eye. Cuts and pastes hands, creates and overlays GUI.
    right_stream = cv2.VideoCapture(0)
    right_stream.set(cv2.CAP_PROP_FPS, 60) # Частота кадров
    right_stream.set(cv2.CAP_PROP_FRAME_WIDTH, 1920) # Ширина кадров в видеопотоке.
    right_stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080) # Высота кадров в видеопотоке.
    prev_frame_time = 0
    new_frame_time = 0
    while True:
        _, img = right_stream.read()
        img = img[0:1024, 500:1670]
        fingers, hands, minx_of_hands, miny_of_hands = detector.find_and_get_hands(img)
        compressed_image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA))
        gui_global = create_GUI(fingers)
        compressed_image.paste(gui_global, [400,0], gui_global)
        if (len(fingers) >= 20):
            compressed_image.paste(hands, [minx_of_hands, miny_of_hands], hands)

        cv2_compressed_image = cv2.cvtColor(np.array(compressed_image), cv2.COLOR_BGRA2RGBA)

        font = cv2.FONT_HERSHEY_SIMPLEX 
        new_frame_time = time.time() 
        fps = 1/(new_frame_time-prev_frame_time) 
        prev_frame_time = new_frame_time 
        fps = int(fps) 
        fps = str(fps) 
        cv2.putText(cv2_compressed_image, fps, (7, 70), font, 3, (100, 255, 0), 3, cv2.LINE_AA) 

        cv2.imshow("Right", cv2_compressed_image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            exit(0)

if __name__ == "__main__": # Runs processes (eye's workers)
    right_process = Process(name='right_process', target=right_work)
    left_process = Process(name='left_process', target=left_work)
    right_process.start()
    left_process.start()
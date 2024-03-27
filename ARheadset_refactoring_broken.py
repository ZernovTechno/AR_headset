import cv2
import mediapipe as mp
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from cvzone.SelfiSegmentationModule import SelfiSegmentation
from multiprocessing import Process
from dataclasses import dataclass, field
import datetime
import time

segmentor = SelfiSegmentation()

def check_in_region(top_left, bottom_right, point):
    if (point[2] > top_left[1]-20 and point[2] < bottom_right[1]+20 and point[1] > top_left[0]-20 and point[1] < bottom_right[0]+20):
        return True
    else:
        return False

class HandDetector():
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
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=False):
        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
        return lmList

detector = HandDetector()

@dataclass
class GUIObject(): # Class interface object.
    active: bool = None # Shows object on next draw
    size: list = field(default_factory=list) # Size of created GUI object
    destination: list = field(default_factory=list) # Destination of created GUI object
    def __post_init__(self): # Post init function. Creates border and background by size param
        self.image = Image.new('RGBA', self.size, (255, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)

clocks = GUIObject(True, size=[200, 100], destination=[400, 100])

def create_GUI(fingers): # Make an interface overlay
    if len(fingers) > 20:
        controller(fingers)

    gui = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))

    if clocks.active:
        clocks.__post_init__()
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M")
        date_str = now.strftime("%d-%m-%Y")
        clocks.draw.rounded_rectangle(((0, 0), clocks.size), 20, fill=(255, 255, 255, 230))
        clocks.draw.text((50, 25), f"{date_str}\n{time_str}", (255, 255, 255), font=ImageFont.truetype("sans-serif.ttf", 30))
    
    gui.paste(clocks.image, clocks.destination, clocks.image)
    return gui

fingers_old = [0, 0, 0, 0]

def controller(fingers): # Get fingers positions and check interface
    big_finger_coordinates = fingers[4] # Большой палец (координаты)
    index_finger_coordinates = fingers[8] # Указательный палец (координаты)
    # ... (Дополнительная логика для других пальцев и взаимодействия с GUI)

    # Example of interaction with GUI element
    if check_in_region(clocks.destination, [clocks.destination[0] + clocks.size[0], clocks.destination[1] + clocks.size[1]], index_finger_coordinates):
        # Logic to move the clocks or interact with it
        pass

    fingers_old = fingers

# Function to process video stream
def process_video_stream(stream_id, window_name):
    # Создаем объекты для детектирования рук и сегментации внутри процесса
    detector = HandDetector()
    segmentor = SelfiSegmentation()

    stream = cv2.VideoCapture(stream_id)
    stream.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    while True:
        ret, image = stream.read()
        if not ret:
            break

        # Crop and process the image
        image = image[0:1024, 600:1770]
        image = detector.findHands(image, draw=True)
        fingers = detector.findPosition(image)

        # Create and overlay the GUI
        gui_image = create_GUI(fingers)
        final_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGBA))
        final_image.paste(gui_image, (0, 0), gui_image)

        # Display the final image
        cv2.imshow(window_name, cv2.cvtColor(np.array(final_image), cv2.COLOR_RGBA2BGR))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    stream.release()
    cv2.destroyAllWindows()

# Main execution
if __name__ == "__main__":
    # Запускаем процессы для каждого видеопотока
    right_process = Process(target=process_video_stream, args=(0, "Right"))
    left_process = Process(target=process_video_stream, args=(1, "Left"))
    right_process.start()
    left_process.start()
    right_process.join()
    left_process.join()

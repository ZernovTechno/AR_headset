import cv2
import mediapipe as mp
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from cvzone.SelfiSegmentationModule import SelfiSegmentation
from multiprocessing import Process
from dataclasses import dataclass, field
import datetime

# Utility function to check if a point is within a given region
def check_in_region(top_left, bottom_right, point):
    x, y = point[1], point[2]
    return top_left[0] <= x <= bottom_right[0] and top_left[1] <= y <= bottom_right[1]

# HandDetector class for detecting and drawing hands
class HandDetector:
    def __init__(self, max_hands=2, detection_confidence=0.5, tracking_confidence=0.5):
        self.hands_detector = mp.solutions.hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )

    def find_hands(self, image, draw=False):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.results = self.hands_detector.process(image_rgb)
        if self.results.multi_hand_landmarks and draw:
            for hand_landmarks in self.results.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(image, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)
        return image

    def find_positions(self, image, hand_no=0):
        lm_list = []
        if self.results.multi_hand_landmarks:
            hand = self.results.multi_hand_landmarks[hand_no]
            for id, lm in enumerate(hand.landmark):
                h, w, _ = image.shape
                lm_list.append([id, int(lm.x * w), int(lm.y * h)])
        return lm_list

    def __del__(self):
        self.hands_detector.close()

# GUIObject class for creating GUI elements
@dataclass
class GUIObject:
    active: bool = False
    size: list = field(default_factory=lambda: [200, 100])
    destination: list = field(default_factory=lambda: [400, 100])

    def __post_init__(self):
        self.image = Image.new('RGBA', self.size, (255, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)

# Function to create the GUI
def create_gui(detector, fingers):
    gui = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
    clocks = GUIObject(True, [200, 100], [400, 100])
    clocks.__post_init__()
    now = datetime.datetime.now()
    date_str = now.strftime("%d-%m-%Y")
    time_str = now.strftime("%H:%M")
    clocks.draw.rounded_rectangle(((0, 0), clocks.size), 20, fill=(255, 255, 255, 230))
    font_path = "sans-serif.ttf"
    font_size = 30
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()
    clocks.draw.text((60, 35), f"{date_str}\n{time_str}", (255, 255, 255), font=font)
    gui.paste(clocks.image, clocks.destination, clocks.image)
    return gui

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
        image = detector.find_hands(image, draw=True)
        fingers = detector.find_positions(image)

        # Create and overlay the GUI
        gui_image = create_gui(detector, fingers)
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

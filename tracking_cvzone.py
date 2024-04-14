from cvzone.SelfiSegmentationModule import SelfiSegmentation
from cvzone.HandTrackingModule import HandDetector
import cv2
from PIL import Image, ImageDraw, ImageFont

segmentor = SelfiSegmentation()  # remove background
hand_detector = HandDetector()

class controller():

    def find_and_get_hands(self, img):
        hands, frame = hand_detector.findHands(img, draw=False, flipType=False)
        if hands:
            hand1 = hands[0]  # Get the first hand detected
            landmark = hand1["lmList"]  # List of 21 landmarks for the first hand
            bbox = hand1["bbox"]  # Bounding box around the first hand (x,y,w,h coordinates)
            min_x = bbox[0] - 40
            max_x = bbox[0] + bbox[2] + 40
            min_y = bbox[1] - 40
            max_y = bbox[1] + bbox[3] + 40
            if min_x <= 0:
                min_x = 0
            if min_y <= 0:
                min_y = 0

            crop_img = frame[min_y:max_y, min_x:max_x]
            #src = segmentor.removeBG(crop_img, (0, 0, 0), 0.3)
            _, alpha = cv2.threshold(cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY), 0, 255, cv2.THRESH_BINARY)
            frame[min_y:max_y, min_x:max_x][alpha != 0] = crop_img[alpha != 0]
        return frame
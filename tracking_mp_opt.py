import mediapipe as mp
import cv2
import numpy as np
from cvzone.SelfiSegmentationModule import SelfiSegmentation

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=1,
                       min_detection_confidence=0.5,
                       min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

segmentor = SelfiSegmentation()
class controller():
    def remove_background(self,img):
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        ret, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_TRIANGLE) 
        mask = cv2.bitwise_not(mask)
        kernel = np.ones((9,9), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        result = img.copy()
        result = cv2.cvtColor(result, cv2.COLOR_BGR2BGRA)
        result[:, :, 3] = mask

        return result, mask
    
    def find_and_get_hands(self, image):
        results = hands.process(image)

        lmList = []
        miny = 0
        minx = 0
        maxy = 0
        maxx = 0
        mask = 0
        if results.multi_hand_landmarks:
            myHand = results.multi_hand_landmarks[0]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = image.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
        if (len(lmList) >= 20):
            xlist = []
            ylist = []

            for ids in lmList:
                xlist.append(ids[1])
                ylist.append(ids[2])

            minx = min(xlist) - 40
            maxx = max(xlist) + 40
            miny = min(ylist) - 40
            maxy = max(ylist) + 40
            if (minx <= 0): minx = 1
            if (maxx <= 0): maxx = 1
            if (maxy <= 0): maxy = 1
            if (miny <= 0): miny = 1

            image = image[miny:maxy, minx:maxx]
            image, mask = self.remove_background(image)    
        return image, lmList, miny, minx, maxy, maxx, mask
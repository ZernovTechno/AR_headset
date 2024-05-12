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
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
            _, mask = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU) 
            mask = cv2.bitwise_not(mask)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))

            result = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
            result[:, :, 3] = mask

            return result, mask
        except:
            return img, img
            pass
    
    def find_and_get_hands(self, image):
        results = hands.process(image)

        lmList = []
        miny, minx, maxy, maxx = 0, 0, 0, 0
        mask = 0

        if results.multi_hand_landmarks:
            myHand = results.multi_hand_landmarks[0]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = image.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])

        if len(lmList) >= 20:
            lmArray = np.array(lmList)
            xlist = lmArray[:, 1]
            ylist = lmArray[:, 2]

            minx = np.clip(np.min(xlist) - 30, 1, None)
            maxx = np.clip(np.max(xlist) + 30, 1, None)
            miny = np.clip(np.min(ylist) - 30, 1, None)
            maxy = np.clip(np.max(ylist) + 30, 1, None)

            image = image[miny:maxy, minx:maxx]
            image, mask = self.remove_background(image)

        return image, lmList, miny, minx, maxy, maxx, mask

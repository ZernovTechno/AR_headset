from cvzone.SelfiSegmentationModule import SelfiSegmentation
import mediapipe as mp
import cv2
from PIL import Image, ImageDraw, ImageFont

segmentor = SelfiSegmentation()

class controller():
    def __init__(self, mode=True, maxHands=1, modelComplex=2, detectionCon=0.7, trackCon=0.5):
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
    
    def remove_background(capture):
        result2 = segmentor.removeBG(capture, (0, 0, 0), 0.08)
        src = result2
        tmp = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        _,alpha = cv2.threshold(tmp,0,255,cv2.THRESH_BINARY)
        b, g, r = cv2.split(src)
        rgba = [b,g,r, alpha]
        dst = cv2.merge(rgba,4)
        return dst

    def find_and_get_hands(self):
        img_hands = cropimgwithoutbg
        img_hands = self.findHands(img_hands)
        fingers = self.findPosition(img_hands)
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
            cropimgwithoutbg = self.remove_background(cropimg)    
            hand_image = Image.fromarray(cv2.cvtColor(cropimgwithoutbg, cv2.COLOR_BGRA2RGBA))
        return hand_image

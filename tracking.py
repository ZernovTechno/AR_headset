from cvzone.SelfiSegmentationModule import SelfiSegmentation
import mediapipe as mp
import cv2
# from PIL import Image, ImageDraw, ImageFont

segmentor = SelfiSegmentation()


class Controller:
    def __init__(self, mode=True, max_hands=1, model_complex=2, detection_con=0.7, track_con=0.5):
        self.results = None
        self.mode = mode
        self.maxHands = max_hands
        self.modelComplex = model_complex
        self.detectionCon = detection_con
        self.trackCon = track_con
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.modelComplex, self.detectionCon, self.trackCon)

        self.mpDraw = mp.solutions.drawing_utils

    def find_hands(self, img, draw=False):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        # print(self.results.multi_hand_landmarks)
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
        return img

    def find_position(self, img, hand_num=0, draw=False):
        lm_list = []
        if self.results.multi_hand_landmarks:
            my_hand = self.results.multi_hand_landmarks[hand_num]
            for _id, lm in enumerate(my_hand.landmark):
                # print(_id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                # print(_id, cx, cy)
                lm_list.append([_id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
        return lm_list

    # def remove_background(self, capture):
    #     result2 = segmentor.removeBG(capture, (0, 0, 0), 0.08)
    #     src = result2
    #     tmp = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    #     _, alpha = cv2.threshold(tmp, 0, 255, cv2.THRESH_BINARY)
    #     b, g, r = cv2.split(src)
    #     rgba = [b, g, r, alpha]
    #     dst = cv2.merge(rgba, 4)
    #     return dst, dst

    # def find_and_get_hands(self):
    #     img_hands = cropimgwithoutbg
    #     img_hands = self.findHands(img_hands)
    #     fingers = self.findPosition(img_hands)
    #     minx = 0
    #     miny = 0
    #     lmList = [0]
    #     if (len(fingers) >= 20):
    #         xlist = [0]
    #         ylist = [0]
    #
    #         for ids in fingers:
    #             xlist.append(ids[1])
    #             ylist.append(ids[2])
    #
    #         minx = min(xlist) - 80
    #         maxx = max(xlist) + 80
    #         miny = min(ylist) - 80
    #         maxy = max(ylist) + 80
    #         if (minx <= 0): minx = 1
    #         if (maxx <= 0): maxx = 1
    #         if (maxy <= 0): maxy = 1
    #         if (miny <= 0): miny = 1
    #
    #         cropimg = cropimgwithoutbg[miny:maxy, minx:maxx]
    #         cropimgwithoutbg, mask = self.remove_background(cropimg)
    #         hand_image = cropimgwithoutbg
    #     return hand_image, lmList, miny, minx, maxy, maxx, mask

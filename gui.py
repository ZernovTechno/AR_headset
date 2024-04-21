import numpy as np
from PIL import Image, ImageDraw
import applications.base_interface as base_interface

right_panel = base_interface.right_panel(active=True)

class gui_machine():
    right_region: bool =  False
    middle_region: bool = False
    left_region: bool =   False

    right_region_coordinates: list =  [(900,600), (1100,1400)]
    middle_region_coordinates: list = [(700,600), (900,1400)]
    left_region_coordinates: list =   [(500,600), (700,1400)]
    all_region_coordinates: list =    [(500,600), (1100,1400)]

    def check_in_region(self, top_left, bottom_right, point):
        if (point[2] > top_left[1] and point[2] < bottom_right[1] and point[1] > top_left[0] and point[1] < bottom_right[0]): # Check if point coordinates inside the region
            return True
        else:
            return False

    def __init__(self):
        pass

    def create_GUI (self, fingers): # Make an interface overlay
        gui = Image.new('RGBA', (1228, 1440), (0,0,0,0))

        if (len(fingers) > 20):
            self.controller(fingers)
            hand_image = Image.open('applications/resources/hand_icon.png')
            gui.paste(hand_image, (1100, 72), hand_image)

        self.draw = ImageDraw.Draw(gui)
        if (right_panel.active):
            right_panel_image = right_panel.main()
            gui.paste(right_panel_image, right_panel.destination, right_panel_image)

        return gui

    def controller(self, fingers): # Get fingers positions and check interface

        big_finger_coordinates = fingers[4] # Большой палец (координаты)
        index_finger_coordinates = fingers[8] # Указательный палец (координаты)
        middle_finger_coordinates = fingers[12] # Средний палец (координаты) 
        ring_finger_coordinates = fingers[16] # Безымянный палец (координаты)
        pinky_finger_coordinates = fingers[20] # Мизинец (координаты)
        #if (abs(big_finger_coordinates[1] - index_finger_coordinates[1]) < 60 and abs(big_finger_coordinates[2] - index_finger_coordinates[2]) < 60): # Check, if index finger near the big finger
        if (self.check_in_region(self.all_region_coordinates[0], self.all_region_coordinates[1], index_finger_coordinates)):
            
            self.draw.rectangle(self.all_region_coordinates, outline=(255,255,255, 150))
            
            if (self.check_in_region(self.right_region_coordinates[0], self.right_region_coordinates[1], index_finger_coordinates) and not self.right_region):
                self.right_region = True
                print("1 ready")
            if (self.check_in_region(self.middle_region_coordinates[0], self.middle_region_coordinates[1], index_finger_coordinates) and not self.middle_region and self.right_region):
                self.middle_region = True 
                print("2 ready")   
            if (self.check_in_region(self.left_region_coordinates[0], self.left_region_coordinates[1], index_finger_coordinates) and not self.left_region and self.middle_region and self.right_region):
                self.left_region = True
                print("3 ready")
        else:
            self.right_region = False
            self.middle_region = False
            self.left_region = False

        if (self.right_region and self.middle_region and self.left_region):
            right_panel.active = not right_panel.active
            self.right_region = False
            self.middle_region = False
            self.left_region = False
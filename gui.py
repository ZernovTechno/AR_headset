import numpy as np
from PIL import Image, ImageDraw, ImageFont
import applications.base_interface as base_interface
import applications.calculator as calculator
import applications.apps_panel as apps_panel
import applications.clock as clock
import applications.paint as paint
import applications.keyboard as keyboard
import applications.settings as settings
import cv2

calc = calculator.calc(active=False)
clocks = clock.pane(active=False)
paint_app = paint.pane(active=False)
keyboard_app = keyboard.pane(active=False)
settings_app = settings.pane(active=False)

right_panel = base_interface.right_panel(active=True)
apps = apps_panel.panel(active=False)

class gui_machine():
    messaging: bool =   True
    message: str = "Добро пожаловать!"
    message_color: list = (0,255,0,200)
    message_iteration: int = 0

    right_region: bool =  False
    middle_region: bool = False
    left_region: bool =   False

    right_region_coordinates: list =  [(900,800), (1100,1400)]
    middle_region_coordinates: list = [(700,800), (900,1400)]
    left_region_coordinates: list =   [(500,800), (700,1400)]
    all_region_coordinates: list =    [(500,800), (1100,1400)]

    def check_in_region(self, top_left, bottom_right, point):
        if (point[2] > top_left[1] and point[2] < bottom_right[1] and point[1] > top_left[0] and point[1] < bottom_right[0]): # Check if point coordinates inside the region
            return True
        else:
            return False

    def __init__(self):
        pass

    def create_message(self,text, color):
        self.messaging = True
        self.message_iteration = 0
        self.message = text
        self.message_color = color

    def create_GUI (self, fingers, distance, xdegrees, config): # Make an interface overlay
        gui = Image.new('RGBA', (5184, 5184), (0,0,0,0))
        self.left_gui = Image.new('RGBA', (1440, 1440), (0,0,0,0))
        self.right_gui = Image.new('RGBA', (1440, 1440), (0,0,0,0))
        self.draw = ImageDraw.Draw(gui)
        if (xdegrees > 260):
            xdegrees = xdegrees - 360
        self.plus_pixels_by_x = int(xdegrees * 14.4)

        if (self.messaging):
            if (self.message_iteration > 300):
                self.messaging = False
                self.message_iteration = 0
            else:
                self.message_iteration += 1
                self.draw.text(((1480//2), (200)),self.message,self.message_color,font=ImageFont.truetype("applications/resources/sans-serif.ttf", 45))
                

        if (len(fingers) > 20):
            self.controller(fingers, distance, config)
            hand_image = Image.open('applications/resources/hand_icon.png')
            gui.paste(hand_image, (1150, 172), hand_image)

        if (right_panel.active):
            right_panel_image = right_panel.main()
            gui.paste(right_panel_image, right_panel.destination, right_panel_image)
        if (calc.active):
            calc_image = calc.main()
            gui.paste(calc_image, calc.destination, calc_image)
        if (apps.active):
            apps_image = apps.main()
            gui.paste(apps_image, apps.destination, apps_image)
        if (clocks.active):
            clocks_image = clocks.main()
            gui.paste(clocks_image, clocks.destination, clocks_image)
        if (paint_app.active):
            paint_image = paint_app.main()
            gui.paste(paint_image, paint_app.destination, paint_image)
        if (keyboard_app.active):
            keyboard_image = keyboard_app.main()
            gui.paste(keyboard_image, keyboard_app.destination, keyboard_image)
        if (settings_app.active):
            settings_image = settings_app.main(config)
            gui.paste(settings_image, settings_app.destination, settings_image)
        self.calculated_x = int(config["Customize"]["to_interface_range"])//2
        self.left_gui.paste(gui, (0+self.calculated_x-self.plus_pixels_by_x,0), gui)
        self.right_gui.paste(gui, (0-self.calculated_x-self.plus_pixels_by_x,0), gui)
        
        if config["Options"]["barrel_distortion"] == "True":
            return cv2.cvtColor(np.array(self.left_gui), cv2.COLOR_BGRA2RGB), cv2.cvtColor(np.array(self.right_gui), cv2.COLOR_BGRA2RGB)
        else:
            return self.left_gui, self.right_gui

    def controller(self, fingers, distance, config): # Get fingers positions and check interface

        big_finger_coordinates = fingers[4] # Большой палец (координаты)
        index_finger_coordinates = fingers[int(config["Customize"]["index_finger"])] # Указательный палец (координаты)
        middle_finger_coordinates = fingers[12] # Средний палец (координаты) 
        ring_finger_coordinates = fingers[16] # Безымянный палец (координаты)
        pinky_finger_coordinates = fingers[20] # Мизинец (координаты)
        index_finger_coordinates[1]-= self.calculated_x - self.plus_pixels_by_x
        #if (abs(big_finger_coordinates[1] - index_finger_coordinates[1]) < 60 and abs(big_finger_coordinates[2] - index_finger_coordinates[2]) < 60): # Check, if index finger near the big finger
        if (self.check_in_region(self.all_region_coordinates[0], self.all_region_coordinates[1], index_finger_coordinates)):
            
            self.draw.rectangle(self.all_region_coordinates, outline=(255,255,255, 150))
            
            if (self.check_in_region(self.right_region_coordinates[0], self.right_region_coordinates[1], index_finger_coordinates) and not self.right_region):
                self.right_region = True
            if (self.check_in_region(self.middle_region_coordinates[0], self.middle_region_coordinates[1], index_finger_coordinates) and not self.middle_region and self.right_region):
                self.middle_region = True 
            if (self.check_in_region(self.left_region_coordinates[0], self.left_region_coordinates[1], index_finger_coordinates) and not self.left_region and self.middle_region and self.right_region):
                self.left_region = True
        else:
            self.right_region = False
            self.middle_region = False
            self.left_region = False

        if (self.right_region and self.middle_region and self.left_region):
            right_panel.active = not right_panel.active
            self.right_region = False
            self.middle_region = False
            self.left_region = False

        if (abs(big_finger_coordinates[1]-(self.calculated_x- self.plus_pixels_by_x) - index_finger_coordinates[1]) < 60 and abs(big_finger_coordinates[2] - index_finger_coordinates[2]) < 60): # Check, if index finger near the big finger
        # if index near big.
            if (self.check_in_region(calc.destination, [calc.destination[0] + calc.size[0], calc.destination[1] + calc.size[1]], index_finger_coordinates) and calc.active): # Check, if index finger inside the clocks
                calc.destination = [index_finger_coordinates[1]-calc.size[0]//2, index_finger_coordinates[2]-calc.size[1]//2] # Set the center of clocks to the index finger
            elif (self.check_in_region(clocks.destination, [clocks.destination[0] + clocks.size[0], clocks.destination[1] + clocks.size[1]], index_finger_coordinates) and clocks.active): # Check, if index finger inside the clocks
                clocks.destination = [index_finger_coordinates[1]-clocks.size[0]//2, index_finger_coordinates[2]-clocks.size[1]//2] # Set the center of clocks to the index finger
            elif (self.check_in_region(paint_app.destination, [paint_app.destination[0] + paint_app.size[0], paint_app.destination[1] + paint_app.size[1]], index_finger_coordinates) and paint_app.active): # Check, if index finger inside the clocks
                paint_app.destination = [index_finger_coordinates[1]-paint_app.size[0]//2, index_finger_coordinates[2] - paint_app.size[1] + 50] # Set the center of clocks to the index finger
            elif (self.check_in_region(keyboard_app.destination, [keyboard_app.destination[0] + keyboard_app.size[0], keyboard_app.destination[1] + keyboard_app.size[1]], index_finger_coordinates) and keyboard_app.active): # Check, if index finger inside the clocks
                keyboard_app.destination = [index_finger_coordinates[1]-keyboard_app.size[0]//2, index_finger_coordinates[2] - keyboard_app.size[1]//2] # Set the center of clocks to the index finger
            elif (self.check_in_region(settings_app.destination, [settings_app.destination[0] + settings_app.size[0], settings_app.destination[1] + settings_app.size[1]], index_finger_coordinates) and settings_app.active): # Check, if index finger inside the clocks
                settings_app.destination = [index_finger_coordinates[1]-settings_app.size[0]//2, index_finger_coordinates[2] - settings_app.size[1]+50] # Set the center of clocks to the index finger
        
        elif (self.check_in_region(right_panel.destination, [right_panel.destination[0] + right_panel.size[0], right_panel.destination[1] + right_panel.size[1]], index_finger_coordinates) and right_panel.active): # Check, if index finger inside the clocks
                self.command_receiver(right_panel.controller([index_finger_coordinates[1]-right_panel.destination[0], index_finger_coordinates[2]-right_panel.destination[1]]))
        elif (self.check_in_region(apps.destination, [apps.destination[0] + apps.size[0], apps.destination[1] + apps.size[1]], index_finger_coordinates) and apps.active): # Check, if index finger inside the clocks
                self.command_receiver(apps.controller([index_finger_coordinates[1]-apps.destination[0], index_finger_coordinates[2]-apps.destination[1]]))
        elif (self.check_in_region(paint_app.destination, [paint_app.destination[0] + paint_app.size[0], paint_app.destination[1] + paint_app.size[1]], index_finger_coordinates) and paint_app.active): # Check, if index finger inside the clocks
            self.command_receiver(paint_app.controller([index_finger_coordinates[1]-paint_app.destination[0], index_finger_coordinates[2]-paint_app.destination[1]]))
        elif (self.check_in_region(keyboard_app.destination, [keyboard_app.destination[0] + keyboard_app.size[0], keyboard_app.destination[1] + keyboard_app.size[1]], index_finger_coordinates) and keyboard_app.active): # Check, if index finger inside the clocks
            self.command_receiver(keyboard_app.controller([index_finger_coordinates[1]-keyboard_app.destination[0], index_finger_coordinates[2]-keyboard_app.destination[1]]))
        elif (self.check_in_region(settings_app.destination, [settings_app.destination[0] + settings_app.size[0], settings_app.destination[1] + settings_app.size[1]], index_finger_coordinates) and settings_app.active): # Check, if index finger inside the clocks
            self.command_receiver(settings_app.controller([index_finger_coordinates[1]-settings_app.destination[0], index_finger_coordinates[2]-settings_app.destination[1]], config))


    def command_receiver(self, command):
        match command:
            case "run_calc":
                calc.active = not calc.active
            case "run_appspanel":
                apps.active = not apps.active
            case "run_keyboard":
                keyboard_app.active = not keyboard_app.active
            case "run_video":
                self.create_message("Пока не работает", (255,0,0,255))
            case "run_compose":
                paint_app.active = not paint_app.active
            case "run_clock":
                clocks.active = not clocks.active
            case "run_computer":
                self.create_message("Пока не работает", (255,0,0,255))
            case "run_folder":
                self.create_message("Пока не работает", (255,0,0,255))
            case "run_settings":
                settings_app.active = not settings_app.active

            case "not_working":
                self.create_message("Пока не работает", (255,0,0,255))
            case "exit":
                exit()
            case _:
                pass


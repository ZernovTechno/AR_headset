# import numpy as np
from PIL import Image, ImageDraw, ImageFont
# import time
import applications.base_interface as base_interface
import applications.calculator as calculator
import applications.apps_panel as apps_panel
import applications.clock as clock
import applications.paint as paint
import applications.keyboard as keyboard

right_panel = base_interface.right_panel(active=True)
calc = calculator.calc(active=False)
apps = apps_panel.panel(active=False)
clocks = clock.pane(active=False)
paint_app = paint.pane(active=False)
keyboard_app = keyboard.pane(active=False)


class GUIMachine:
    messaging: bool = True
    message: str = "Добро пожаловать!"
    message_color: list = (0, 255, 0, 200)
    message_iteration: int = 0
    draw = ImageDraw.Draw(Image.new('RGBA', (1480, 1440), (0, 0, 0, 0)))

    right_region: bool = False
    middle_region: bool = False
    left_region: bool = False

    right_region_coordinates: list = [(900, 800), (1100, 1400)]
    middle_region_coordinates: list = [(700, 800), (900, 1400)]
    left_region_coordinates: list = [(500, 800), (700, 1400)]
    all_region_coordinates: list = [(500, 800), (1100, 1400)]

    @staticmethod
    def check_in_region(top_left, bottom_right, point):
        if (top_left[1] < point[2] < bottom_right[1]
                and top_left[0] < point[1] < bottom_right[0]):  # Check if point coordinates inside the region
            return True
        else:
            return False

    def __init__(self):
        pass

    def create_message(self, text, color):
        self.messaging = True
        self.message_iteration = 0
        self.message = text
        self.message_color = color

    def create_gui(self, fingers):  # Make an interface overlay
        gui = Image.new('RGBA', (1480, 1440), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(gui)

        if self.messaging:
            if self.message_iteration > 700:
                self.messaging = False
                self.message_iteration = 0
            else:
                self.message_iteration += 1
                self.draw.text(((1480 // 3), 50), self.message, self.message_color,
                               font=ImageFont.truetype("applications/resources/sans-serif.ttf", 45))

        if len(fingers) > 20:
            self.controller(fingers)
            hand_image = Image.open('applications/resources/hand_icon.png')
            gui.paste(hand_image, (1100, 72), hand_image)

        if right_panel.active:
            right_panel_image = right_panel.main()
            gui.paste(right_panel_image, right_panel.destination, right_panel_image)
        if calc.active:
            calc_image = calc.main()
            gui.paste(calc_image, calc.destination, calc_image)
        if apps.active:
            apps_image = apps.main()
            gui.paste(apps_image, apps.destination, apps_image)
        if clocks.active:
            clocks_image = clocks.main()
            gui.paste(clocks_image, clocks.destination, clocks_image)
        if paint_app.active:
            paint_image = paint_app.main()
            gui.paste(paint_image, paint_app.destination, paint_image)
        if keyboard_app.active:
            keyboard_image = keyboard_app.main()
            gui.paste(keyboard_image, keyboard_app.destination, keyboard_image)

        return gui

    def controller(self, fingers):  # Get fingers positions and check interface

        big_finger_coordinates = fingers[4]  # Большой палец (координаты)
        index_finger_coordinates = fingers[8]  # Указательный палец (координаты)
        # middle_finger_coordinates = fingers[12]  # Средний палец (координаты)
        # ring_finger_coordinates = fingers[16]  # Безымянный палец (координаты)
        # pinky_finger_coordinates = fingers[20]  # Мизинец (координаты)
        # if (abs(big_finger_coordinates[1] - index_finger_coordinates[1]) < 60 and abs(big_finger_coordinates[2] -
        # index_finger_coordinates[2]) < 60): # Check, if index finger near the big finger
        if (
                self.check_in_region(self.all_region_coordinates[0], self.all_region_coordinates[1],
                                     index_finger_coordinates)):

            self.draw.rectangle(self.all_region_coordinates, outline=(255, 255, 255, 150))

            if (self.check_in_region(self.right_region_coordinates[0], self.right_region_coordinates[1],
                                     index_finger_coordinates) and not self.right_region):
                self.right_region = True
            if (self.check_in_region(self.middle_region_coordinates[0], self.middle_region_coordinates[1],
                                     index_finger_coordinates) and not self.middle_region and self.right_region):
                self.middle_region = True
            if (self.check_in_region(self.left_region_coordinates[0], self.left_region_coordinates[1],
                                     index_finger_coordinates) and not self.left_region and self.middle_region
                    and self.right_region):
                self.left_region = True
        else:
            self.right_region = False
            self.middle_region = False
            self.left_region = False

        if self.right_region and self.middle_region and self.left_region:
            right_panel.active = not right_panel.active
            self.right_region = False
            self.middle_region = False
            self.left_region = False

        if (abs(big_finger_coordinates[1] - index_finger_coordinates[1]) < 60 and abs(
                big_finger_coordinates[2] - index_finger_coordinates[
                    2]) < 60):  # Check, if index finger near the big finger
            # if index near big.
            if (self.check_in_region(calc.destination,
                                     [calc.destination[0] + calc.size[0], calc.destination[1] + calc.size[1]],
                                     index_finger_coordinates)
                    and calc.active):  # Check, if index finger inside the clocks
                calc.destination = [index_finger_coordinates[1] - calc.size[0] // 2,
                                    index_finger_coordinates[2] - calc.size[
                                        1] // 2]  # Set the center of clocks to the index finger
            elif (self.check_in_region(clocks.destination,
                                       [clocks.destination[0] + clocks.size[0], clocks.destination[1] + clocks.size[1]],
                                       index_finger_coordinates)
                  and clocks.active):  # Check, if index finger inside the clocks
                clocks.destination = [index_finger_coordinates[1] - clocks.size[0] // 2,
                                      index_finger_coordinates[2] - clocks.size[
                                          1] // 2]  # Set the center of clocks to the index finger
            elif (self.check_in_region(paint_app.destination, [paint_app.destination[0] + paint_app.size[0],
                                                               paint_app.destination[1] + paint_app.size[1]],
                                       index_finger_coordinates)
                  and paint_app.active):  # Check, if index finger inside the clocks
                paint_app.destination = [index_finger_coordinates[1] - paint_app.size[0] // 2,
                                         index_finger_coordinates[2] - paint_app.size[
                                             1] + 50]  # Set the center of clocks to the index finger
            elif (self.check_in_region(keyboard_app.destination, [keyboard_app.destination[0] + keyboard_app.size[0],
                                                                  keyboard_app.destination[1] + keyboard_app.size[1]],
                                       index_finger_coordinates)
                  and keyboard_app.active):  # Check, if index finger inside the clocks
                keyboard_app.destination = [index_finger_coordinates[1] - keyboard_app.size[0] // 2,
                                            index_finger_coordinates[2] - keyboard_app.size[
                                                1] // 2]  # Set the center of clocks to the index finger

        elif (self.check_in_region(right_panel.destination, [right_panel.destination[0] + right_panel.size[0],
                                                             right_panel.destination[1] + right_panel.size[1]],
                                   index_finger_coordinates)
              and right_panel.active):  # Check, if index finger inside the clocks
            self.command_receiver(right_panel.controller([index_finger_coordinates[1] - right_panel.destination[0],
                                                          index_finger_coordinates[2] - right_panel.destination[1]]))
        elif (self.check_in_region(apps.destination,
                                   [apps.destination[0] + apps.size[0], apps.destination[1] + apps.size[1]],
                                   index_finger_coordinates)
              and apps.active):  # Check, if index finger inside the clocks
            self.command_receiver(apps.controller(
                [index_finger_coordinates[1] - apps.destination[0], index_finger_coordinates[2] - apps.destination[1]]))
        elif (self.check_in_region(paint_app.destination, [paint_app.destination[0] + paint_app.size[0],
                                   paint_app.destination[1] + paint_app.size[1]], index_finger_coordinates)
              and paint_app.active):  # Check, if index finger inside the clocks
            self.command_receiver(paint_app.controller([index_finger_coordinates[1] - paint_app.destination[0],
                                                        index_finger_coordinates[2] - paint_app.destination[1]]))
        elif (self.check_in_region(keyboard_app.destination, [keyboard_app.destination[0] + keyboard_app.size[0],
                                   keyboard_app.destination[1] + keyboard_app.size[1]], index_finger_coordinates)
              and keyboard_app.active):  # Check, if index finger inside the clocks
            self.command_receiver(keyboard_app.controller([index_finger_coordinates[1] - keyboard_app.destination[0],
                                                           index_finger_coordinates[2] - keyboard_app.destination[1]]))

    def command_receiver(self, command):
        match command:
            case "run_calc":
                apps.active = not apps.active
                calc.active = not calc.active
            case "run_appspanel":
                apps.active = not apps.active
            case "run_keyboard":
                apps.active = not apps.active
                keyboard_app.active = not keyboard_app.active
            case "run_video":
                self.create_message("Пока не работает", (255, 0, 0, 255))
            case "run_compose":
                apps.active = not apps.active
                paint_app.active = not paint_app.active
            case "run_clock":
                apps.active = not apps.active
                clocks.active = not clocks.active
            case "run_computer":
                self.create_message("Пока не работает", (255, 0, 0, 255))
            case "run_folder":
                self.create_message("Пока не работает", (255, 0, 0, 255))
            case "not_working":
                self.create_message("Пока не работает", (255, 0, 0, 255))
            case _:
                pass

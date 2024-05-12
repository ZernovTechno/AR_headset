from PIL import Image, ImageDraw
from dataclasses import dataclass, field
calc_icon = Image.open('applications/resources/calculator.png')
clock_icon = Image.open('applications/resources/clock.png')
keyboard_icon = Image.open('applications/resources/keyboard.png')
video_icon = Image.open('applications/resources/video.png')
compose_icon = Image.open('applications/resources/paintbrush2.png')
folder_icon = Image.open('applications/resources/folder.png')
computer_icon = Image.open('applications/resources/computer.png')
@dataclass
class panel():
    """Тип данных объект интерфейса"""
    active: bool = None # Shows object on next draw
    size: int = (700, 330)
    destination: int = (600, 500)
    button_timer: int = 0
    def check_in_region(self, top_left, bottom_right, point):
        if (point[1] > top_left[1] and point[1] < bottom_right[1] and point[0] > top_left[0] and point[0] < bottom_right[0]): # Check if point coordinates inside the region
            return True
        else:
            return False
        
    def main(self):
        self.image = Image.new('RGBA', self.size, (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)
        
        self.image.paste(calc_icon, (0, 0), calc_icon)
        self.image.paste(clock_icon, (200, 0), clock_icon)
        self.image.paste(keyboard_icon, (400, 0), keyboard_icon)
        self.image.paste(folder_icon, (600, 0), folder_icon)
        self.image.paste(video_icon, (100, 200), video_icon)
        self.image.paste(compose_icon, (300, 200), compose_icon)
        self.image.paste(computer_icon, (500, 200), computer_icon)
        return self.image
    def controller (self, coordinates): # Здесь пишем что исполняется по нажатию на кнопку. При этом coordinates - координата указательного пальца НА ПОЛОТНЕ ОБЪЕКТА (self.size)
        if (self.check_in_region([0,0], [128,128], coordinates)):
            if (self.button_timer > 20):
                self.button_timer = 0
                return "run_calc"
            else:
                self.button_timer += 1
        elif (self.check_in_region([200,0], [328,128], coordinates)):
            if (self.button_timer > 20):
                self.button_timer = 0
                return "run_clock"
            else:
                self.button_timer += 1
        elif (self.check_in_region([400,0], [528,128], coordinates)):
            if (self.button_timer > 20):
                self.button_timer = 0
                return "run_keyboard"
            else:
                self.button_timer += 1
        elif (self.check_in_region([600,0], [728,128], coordinates)):
            if (self.button_timer > 20):
                self.button_timer = 0
                return "run_folder"
            else:
                self.button_timer += 1
        elif (self.check_in_region([100,200], [228,328], coordinates)):
            if (self.button_timer > 20):
                self.button_timer = 0
                return "run_video"
            else:
                self.button_timer += 1
        elif (self.check_in_region([300,200], [428,328], coordinates)):
            if (self.button_timer > 20):
                self.button_timer = 0
                return "run_compose"
            else:
                self.button_timer += 1
        elif (self.check_in_region([500,200], [628,328], coordinates)):
            if (self.button_timer > 20):
                self.button_timer = 0
                return "run_computer"
            else:
                self.button_timer += 1
        else:
            if (self.button_timer > 1): self.button_timer -= 2
        return "nothing"
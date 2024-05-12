from PIL import Image, ImageDraw
from dataclasses import dataclass, field
import time
x_icon = Image.open('applications/resources/x.png')
download_icon = Image.open('applications/resources/download.png')
def check_in_region(top_left, bottom_right, point):
    if (point[1] > top_left[1] and point[1] < bottom_right[1] and point[0] > top_left[0] and point[0] < bottom_right[0]): # Check if point coordinates inside the region
        return True
    else:
        return False
@dataclass
class pane():
    """Тип данных объект интерфейса"""
    active: bool = None # Shows object on next draw
    size: int = (640, 480) # Размер (Не более 1440x1480)
    destination: int = (400, 500) # Расположение на экране (координата на пространстве 1440x1480)
    button_timer: int = 0
    selected_color: list = (0,0,0,255)
    def __init__(self, active):
        self.active = active
        self.painting = Image.new('RGBA', (615, 385), (255, 255, 255, 255))
        self.drawing = ImageDraw.Draw(self.painting)
    def main(self):
        self.image = Image.new('RGBA', self.size, (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)
        self.draw.rounded_rectangle(((0, 0), self.size), 20, fill=(255,255,255,180)) # Здесь рисуем всякое поэлементно
        self.image.paste(self.painting, (15,15), self.painting)
        self.image.paste(x_icon, (560,405), x_icon)
        self.image.paste(download_icon, (470,405), download_icon)
        self.draw.rounded_rectangle(((15, 405), (65, 475)), 20, fill=(255,0,0,200))
        self.draw.rounded_rectangle(((80, 405), (130, 475)), 20, fill=(0,255,0,200))
        self.draw.rounded_rectangle(((145, 405), (195, 475)), 20, fill=(0,0,255,200))
        self.draw.rounded_rectangle(((210, 405), (260, 475)), 20, fill=(0,0,0,200))

        self.image.save("menu.png")

        return self.image
    def controller (self, coordinates): # Здесь пишем что исполняется по нажатию на кнопку. При этом coordinates - координата указательного пальца НА ПОЛОТНЕ ОБЪЕКТА (self.size)
        if (check_in_region([15,15], [615,385], coordinates)): # Check, if index finger inside the clocks
            if (self.button_timer > 5):
                self.button_timer = 0
                self.drawing.ellipse([(coordinates[0], coordinates[1]), (coordinates[0] + 10, coordinates[1] + 10)],self.selected_color, width=7)
            else:
                self.button_timer += 1
        elif (check_in_region([560,405], [630,475], coordinates)):
            if (self.button_timer > 20):
                self.button_timer = 0
                self.drawing.rectangle([(0,0), self.painting.size], fill=(255,255,255,255))
            else:
                self.button_timer += 1
        elif (check_in_region([470,405], [540,475], coordinates)):
            if (self.button_timer > 30):
                self.button_timer = 0
                self.painting.save("saves/painting/painting_" + time.strftime("%d.%m.%Y_%H.%M.%S", time.localtime()) + ".png")
            else:
                self.button_timer += 1
        elif (check_in_region([15,405], [65, 475], coordinates)):
            if (self.button_timer > 20):
                self.button_timer = 0
                self.selected_color = (255,0,0,255)
            else:
                self.button_timer += 1
        elif (check_in_region([80, 405], [130, 475], coordinates)):
            if (self.button_timer > 30):
                self.button_timer = 0
                self.selected_color = (0,255,0,255)
            else:
                self.button_timer += 1
        elif (check_in_region([145, 405], [195, 475], coordinates)):
            if (self.button_timer > 30):
                self.button_timer = 0
                self.selected_color = (0,0,255,255)
            else:
                self.button_timer += 1
        elif (check_in_region([210, 405], [260, 475], coordinates)):
            if (self.button_timer > 30):
                self.button_timer = 0
                self.selected_color = (0,0,0,255)
            else:
                self.button_timer += 1
        else:
            if (self.button_timer > 1): self.button_timer -= 2
        return "ok"
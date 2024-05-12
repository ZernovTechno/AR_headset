from PIL import Image, ImageDraw
from dataclasses import dataclass, field

@dataclass
class right_panel():
    """Тип данных объект интерфейса"""
    active: bool = None # Shows object on next draw
    size: int = (90, 400)
    destination: int = (1300, 500)
    button_timer: int = 0
    def check_in_region(self, top_left, bottom_right, point):
        if (point[1] > top_left[1] and point[1] < bottom_right[1] and point[0] > top_left[0] and point[0] < bottom_right[0]): # Check if point coordinates inside the region
            return True
        else:
            return False
        
    def main(self):
        self.image = Image.new('RGBA', self.size, (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)
        self.draw.rounded_rectangle(((0, 0), self.size), 20, fill=(255,255,255,200))
        self.draw.rounded_rectangle(((10, 10), (80, 80)), 15, fill=(120,120,120,230))
        self.draw.rounded_rectangle(((10, 100), (80, 180)), 15, fill=(120,120,120,230))
        self.draw.rounded_rectangle(((10, 200), (80, 280)), 15, fill=(120,120,120,230))
        self.draw.rounded_rectangle(((10, 300), (80, 380)), 15, fill=(120,120,120,230))

        return self.image
    def controller (self, coordinates): # Здесь пишем что исполняется по нажатию на кнопку. При этом coordinates - координата указательного пальца НА ПОЛОТНЕ ОБЪЕКТА (self.size)
        if (self.check_in_region([10,10], [80,80], coordinates)):
            if (self.button_timer > 20):
                self.button_timer = 0
                self.active = False
                return "run_appspanel"
            else:
                self.button_timer += 1
        else:
            if (self.button_timer > 1): self.button_timer -= 2
        return "nothing"
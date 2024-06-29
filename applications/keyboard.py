from PIL import Image, ImageDraw, ImageFont
from dataclasses import dataclass, field

@dataclass
class pane():
    """Тип данных объект интерфейса"""
    active: bool = None # Shows object on next draw
    size: tuple[int, int] = (860, 300) # Размер (Не более 1440x1480)
    destination: tuple[int, int] = (200, 500) # Расположение на экране (координата на пространстве 1440x1480)
    button_timer: int = 0
    def check_in_region(self, top_left, bottom_right, point):
        if (point[1] > top_left[1] and point[1] < bottom_right[1] and point[0] > top_left[0] and point[0] < bottom_right[0]): # Check if point coordinates inside the region
            return True
        else:
            return False
    def __init__(self, active):
        key_width = 60
        key_height = 70
        padding = 10
        x_offset = 10
        y_offset = 10
        rows = [
            'QWERTYUIOPX',
            'ASDFGHJKL?',
            'ZXCVBNM.,!',
            ' '
        ]
        self.active = active
        self.image = Image.new('RGBA', self.size, (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)
        self.draw.rounded_rectangle(((0, 0), self.size), 20, fill=(255,255,255,200)) # Здесь рисуем всякое поэлементно
        for row_index, row in enumerate(rows):
            for key_index, letter in enumerate(row):
                x = x_offset + key_index * (key_width + padding)
                if row_index == 1:
                    x += (key_width + padding) / 2  # Сдвиг для второго ряда
                elif row_index == 2:
                    x += (key_width + padding)  # Сдвиг для третьего ряда
                elif row_index == 3:
                    x += (key_width *4 + padding)  # Сдвиг для третьего ряда
                    key_width = key_width*3
                y = y_offset + row_index * (key_height + padding)
                self.draw.rectangle([x, y, x + key_width, y + key_height], fill="lightgrey")
                self.draw.text((x + 20, y + 20), letter, fill="black", font=ImageFont.truetype("applications/resources/sans-serif.ttf", 20))
    def main(self):
        return self.image
    def controller (self, coordinates): # Здесь пишем что исполняется по нажатию на кнопку. При этом coordinates - координата указательного пальца НА ПОЛОТНЕ ОБЪЕКТА (self.size)
        if (self.check_in_region([0,0], [860,300], coordinates)):
            if (self.button_timer > 20):
                self.button_timer = 0
                return "not_working"
            else:
                self.button_timer += 1
        return "Nothing"
from PIL import Image, ImageDraw
from dataclasses import dataclass, field

def create_button(draw, coord, text, fill=(200, 200, 200, 230)):
    """Helper function to draw a button"""
    x1, y1, x2, y2 = coord
    draw.rounded_rectangle((x1, y1, x2, y2), 10, fill=fill)
    draw.text((x1 + 10, y1 + 10), text, fill=(0, 0, 0))

@dataclass
class calc():
    """Тип данных объект интерфейса"""
    active: bool = None # Shows object on next draw
    size: int = (300, 400) # Размер (Не более 1440x1480)
    destination: int = (500, 500) # Расположение на экране (координата на пространстве 1440x1480)
    def main(self):
        self.icon = Image.open('applications/resources/calculator.png')
        self.image = Image.new('RGBA', self.size, (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)

        self.draw.rounded_rectangle(((0, 0), self.size), 20, fill=(255,255,255,180)) # Здесь рисуем всякое поэлементно
        self.draw.rounded_rectangle([10, 10, 290, 90], 20, fill=(230,230,230,200))

        buttons = [
            ('7', 10, 100, 80, 160), ('8', 90, 100, 160, 160), ('9', 170, 100, 240, 160),
            ('+', 250, 100, 290, 160),
            ('4', 10, 170, 80, 230), ('5', 90, 170, 160, 230), ('6', 170, 170, 240, 230),
            ('-', 250, 170, 290, 230),
            ('1', 10, 240, 80, 300), ('2', 90, 240, 160, 300), ('3', 170, 240, 240, 300),
            ('*', 250, 240, 290, 300),
            ('0', 10, 310, 160, 370), ('=', 170, 310, 240, 370), ('/', 250, 310, 290, 370),
        ]
        for text, x1, y1, x2, y2 in buttons:
            create_button(self.draw, (x1, y1, x2, y2), text)

        return self.image
    def controller (self, coordinates): # Здесь пишем что исполняется по нажатию на кнопку. При этом coordinates - координата указательного пальца НА ПОЛОТНЕ ОБЪЕКТА (self.size)

        self.active = False
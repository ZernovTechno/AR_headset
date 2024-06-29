from PIL import Image, ImageDraw
from dataclasses import dataclass, field

@dataclass
class right_panel():
    """Тип данных объект интерфейса"""
    active: bool = None # Shows object on next draw
    size: tuple[int, int] = (90, 400) # Размер (Не более 1440x1480)
    destination: tuple[int, int] = (900, 500) # Расположение на экране (координата на пространстве 1440x1480)
    def main(self):
        self.image = Image.new('RGBA', self.size, (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)
        self.draw.rounded_rectangle(((0, 0), self.size), 20, fill=(255,255,255,200)) # Здесь рисуем всякое поэлементно

        return self.image
    def controller (self, coordinates): # Здесь пишем что исполняется по нажатию на кнопку. При этом coordinates - координата указательного пальца НА ПОЛОТНЕ ОБЪЕКТА (self.size)

        self.active = False
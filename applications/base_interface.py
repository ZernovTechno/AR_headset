from PIL import Image, ImageDraw
from dataclasses import dataclass, field

@dataclass
class right_panel():
    """Тип данных объект интерфейса"""
    active: bool = None # Shows object on next draw
    size: int = (90, 400)
    destination: int = (900, 500)
    def main(self):
        self.image = Image.new('RGBA', self.size, (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)
        self.draw.rounded_rectangle(((0, 0), self.size), 20, fill=(255,255,255,200))

        return self.image
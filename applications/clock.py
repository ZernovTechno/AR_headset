from PIL import Image, ImageDraw, ImageFont
from dataclasses import dataclass, field
import datetime

@dataclass
class pane():
    """Тип данных объект интерфейса"""
    active: bool = None # Shows object on next draw
    size: tuple[int, int] = (300, 150) # Размер (Не более 1440x1480)
    destination: tuple[int, int] = (500, 500) # Расположение на экране (координата на пространстве 1440x1480)
    def main(self):
        self.image = Image.new('RGBA', self.size, (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)
        now = datetime.datetime.now()
        time = now.strftime("%H:%M")
        data = now.strftime("%d-%m-%Y")
        match now.strftime("%A"):
            case "Monday":
                weekday = "Понедельник"
            case "Tuesday":
                weekday = "Вторник"
            case "Wednesday":
                weekday = "Среда"
            case "Thursday":
                weekday = "Четверг"
            case "Friday":
                weekday = "Понедельник"
            case "Saturday":
                weekday = "Суббота"
            case "Sunday":
                weekday = "Воскресенье"
            case _:
                weekday = "Ошибка"
        self.draw.rounded_rectangle(((0, 0), self.size), 20, fill=(255,255,255, 230))
        self.draw.text(((self.size[0] // 3 -10), (self.size[1] // 3 -30)),weekday,(120,120,120),font=ImageFont.truetype("applications/resources/sans-serif.ttf", 30))
        self.draw.text(((self.size[0] // 3 -30), (self.size[1] // 3)),data,(120,120,120),font=ImageFont.truetype("applications/resources/sans-serif.ttf", 30))
        self.draw.text(((self.size[0] // 2 -55), (self.size[1] // 3 +30)),time,(120,120,120),font=ImageFont.truetype("applications/resources/sans-serif.ttf", 45))
        return self.image
    def controller (self, coordinates): # Здесь пишем что исполняется по нажатию на кнопку. При этом coordinates - координата указательного пальца НА ПОЛОТНЕ ОБЪЕКТА (self.size)
        pass
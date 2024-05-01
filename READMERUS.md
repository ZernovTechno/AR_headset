# AR_headset
## Разработчик - [Zernov](https://www.youtube.com/@zernovtech)
[README.md on english](./README.md)

## Предисловие
Хэй! Это мой код для создания AR/MR шлема (дополненная реальность) на базе Python и Linux. В Python используется MediaPipe (трекинг рук) и OpenCV для видеопотоков.
Разработку я начал около двух месяцев назад, так что эта штуковина ещё не идеальна.
БОльший FPS, который Вы можете получить - около 30-ти. Хотя при этом Вы должны использовать суперкомпьютер NASA, наверное.

# Начнём!

(Проверьте свою версию Python, я рекомендую 3.11)
Перед запуском кода нужно установить зависимости. Вы можете использовать [requirements](requirements.txt) для этого:

```console
pip install -r requirements.txt
```

## Конфигурация

После установки зависимостей, вы можете настроить программу.

В начале кода "AR_HeadSet.py" вы можете найти немного конфигурационных линий:
```python
use_1_camera = True
use_1_cameras_width = 1280
use_1_cameras_height = 720

use_2_cameras = False
use_2_cameras_width = 1280
use_2_cameras_height = 720
use_2_cameras_first = 0
use_2_cameras_second = 1

use_PS5_camera = False

use_PS4_camera = False
...
```

Здесь устанавливается тип камеры. 
use_1_camera - 1 USB UVC камера.\
use_2_cameras - 2 разных USB UVC камеры. Просто камеры, ничего интересного.\
use_PS4_camera - HD (720p) стерео камера, разработанная для PS4. Работает со специальным кабелем и драйвером, который можно найти [тут](https://github.com/Hackinside/PS4-CAMERA-DRIVERS)\
use_PS5_camera - Full HD (1080p) стерео камера для PS5. Не требует переходника, но требует [драйвера](https://github.com/Hackinside/PS5_camera_files)

После установки камеры вы можете выбрать модуль трекинга из списка:
```python
import tracking_mp_opt as tracking #Быстро
# import tracking_cvzone as tracking #Средне
# import tracking_v1 as tracking #Медленно
```
Раскомментируйте один из них.

В конце конфигурационного кода вы можете найти строки отключения/включения видеозаписи, GUI (интерфейса) и веб интерфейс:
```python
active_recording = True

active_gui = True

active_flask = True
```
Это всё. 

## ЗАПУСК

После установки всех конфигурационных переменных вы можете проверить свою вебкамеру и запустить код:
```console
python3.11 AR_HeadSet.py
```
или
```console
python3 AR_HeadSet.py
```

## Конец

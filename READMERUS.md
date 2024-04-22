# AR_headset
## Разработчик - [Zernov](https://www.youtube.com/@zernovtech)
[README.md на английском](./README.md)

## Предисловие
Хэй! Это мой код для создания AR/MR шлема (дополненная реальность) на базе Python и Linux. В Python используется MediaPipe (трекинг рук) и OpenCV для видеопотоков.
Разработку я начал около двух месяцев назад, так что эта штуковина ещё не идеальна.
БОльший FPS, который Вы можете получить - около 30-ти. Хотя при этом Вы должны использовать суперкомпьютер NASA, наверное.

# Начнём!

(Проверьте свою версию Python, я рекомендую 3.12)
Перед запуском кода нужно установить зависимости. Вы можете использовать [requirements](requirements.txt) для этого:

```pip
$ pip install requirements.txt
```

## Конфигурация

После установки зависимостей, вы можете настроить программу.

Вначале кода "AR_HeadSet.py" вы можете найти немного конфигурационных линий:
```python
use_2_cameras = False
use_2_cameras_height = 720
use_2_cameras_width = 1280
use_2_cameras_first = 0
use_2_cameras_second = 1

use_PS5_camera = True

use_PS4_camera = False
```

Здесь устанавливается тип камеры. 
use_2_cameras - 2 разных USB UVC камеры. Просто камеры, ничего интересного.
use_PS4_camera - HD (720p) стерео камера, разработанная для PS4. Работает со специальным кабелем и драйвером, который можно найти [тут](https://github.com/Hackinside/PS4-CAMERA-DRIVERS)
use_PS5_camera - Full HD (1080p) стерео камера для PS5. Не требует переходника, но требует [драйвера](https://github.com/Hackinside/PS5_camera_files)

После установки камеры вы можете выбрать модуль трекинга из списка:
```python
# import tracking_mp_opt as tracking #Быстро
# import tracking_cvzone as tracking #Средне
# import tracking_v1 as tracking #Медленно
```
Раскомментируйте один из них.

В конце конфигурационного кода вы можете найти строки отключения/включения видеозаписи и GUI (интерфейса):
```python
active_recording = False

active_gui = True
```
Это всё. 

## ЗАПУСК

После установки всех конфигурационных переменных вы можете проверить свою вебкамеру и запустить код:
```python
$ python3 AR_HeadSet.py
```
или
```python
$ py AR_HeadSet.py
```

## Конец

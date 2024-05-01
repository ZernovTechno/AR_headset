# AR_headset
## Managed by [Zernov](https://www.youtube.com/@zernovtech)
[README.md на русском](./READMERUS.md)

## About
Hey! This is my own code for creating an AR/MR helmet based on Linux and Python. This thing uses MediaPipe and Cv2 for video streams.
I started it only something like 2 month ago, so it's not so good
Biggest framerate you can get at this code is around 30, so you should use NASA supercomputer, I think.

# Let's begin!

(Be sure you are using Python 3.11)
Before running this code you should install all dependency, so you can use [requirements](requirements.txt) for that:

```console
pip install -r requirements.txt
```

## Configuration

After installing all dependency, you can set config of application.

In the start of code "AR_HeadSet.py" you can find some configuration lines:
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

Here you can set your camera type.
use_1_camera - 1 USB UVC WEBCam.\
use_2_cameras - 2 different USB UVC WEBCam's. Just cameras, nothing interesting.\
use_PS4_camera - HD (720p) stereo camera, made for Playstation 4. Works with cable and [driver](https://github.com/Hackinside/PS4-CAMERA-DRIVERS)\
use_PS5_camera - Full HD (1080p) stereo camera for PS5. Doesn't need a cable, but needs [driver](https://github.com/Hackinside/PS5_camera_files)

After cameras you can choose tracking module from list:
```python
import tracking_mp_opt as tracking #Fast
# import tracking_cvzone as tracking #Medium
# import tracking_v1 as tracking #Slow
```
Uncomment one of them.

In the end of configuration you can turn on/off video recording, GUI and web interface:
```python
active_recording = True

active_gui = True

active_flask = True
```
That's it. 

## RUN

After setting up all configuration variables you can check your webcam(s) and directly run this code:
```console
python3.11 AR_HeadSet.py
```
or
```console
python3 AR_HeadSet.py
```

## The end 

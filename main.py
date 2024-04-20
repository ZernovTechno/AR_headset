import threading

import numpy as np

# import interface
# import tracking_mp_opt
from device_config import camera_size, screen_size
from widgets.fps import FPSCounter
from video.camera import Camera
from video.display import Display


camera_width, camera_height = camera_size
screen_width, screen_height = screen_size

# hand_image = np.zeros([screen_width // 2, screen_height, 4], dtype=np.uint8)
# actual_image = np.zeros([screen_width // 2, screen_height, 3], dtype=np.uint8)
# gui_image = np.zeros([screen_width // 2, screen_height, 4], dtype=np.uint8)
# fingers = [0]


# def gui_job():
#     global fingers
#     global gui_image
#     while True:
#         gui_image = np.array(gui_machine.render_GUI_frame(fingers))
#         cv2.imshow("Eye: GUI", gui_image)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#            exit(0)


# def video_writer():
#     while True:
#         working_with = Image.fromarray(cv2.cvtColor(left_actual_image, cv2.COLOR_RGB2BGR))
#         working_with.paste(gui_image, (0, 0), gui_image)
#         out.write(cv2.cvtColor(np.array(working_with), cv2.COLOR_BGR2RGB))

# detector = tracking_mp_opt.controller()
camera = Camera()
# gui_machine = interface.GUI()


display = Display(camera, None)
display.add_widget(FPSCounter())

# out = cv2.VideoWriter('outpy.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 25, (1480, 1440))


threads = [
    # ['re', display.right.job, None],
    # ['le', display.left.job, None],
    # ['camera', camera.run, None],
    # ['widgets', gui_job, None],
    ['display', display.show_video, None]
    # ["video", video_writer]
]

for i, (name, proc, _) in enumerate(threads):
    thread = threading.Thread(name=name, target=proc)
    thread.start()

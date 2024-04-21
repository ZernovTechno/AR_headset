import threading

from system import System
from video.camera import Camera
from video.display import Display


class Headset:
    """
    Аппаратная конфигурация устройства
    """
    threads: list
    system: System
    camera: Camera
    display: Display

    def __init__(self):
        self.system = System()
        self.camera = Camera()
        self.display = Display(self.camera, self.system)

    def run(self):
        """
        Запустить AR шлем в многопоточном. Выполняется, пока не завершатся все потоки
        @return:
        """
        self.threads = [
            # ['camera', camera.job, None],
            # ['widgets', gui_job, None],
            ['display', self.display.show_video, None]
            # ["video", video_writer]
        ]

        for i, (name, proc, _) in enumerate(self.threads):
            thread = threading.Thread(name=name, target=proc)
            thread.start()
            self.threads[i][-1] = thread

        for name, routine, thread in self.threads:
            thread.join()

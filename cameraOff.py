from time import time


class CameraOff(object):
    """An emulated camera implementation that streams a repeated sequence of
    files 1.jpg, 2.jpg and 3.jpg at a rate of one frame per second."""

    def __init__(self):
        self.frames = open('./static/img/camoff.jpg', 'rb').read()

    def get_frame(self):
        return self.frames[int(time()) % 1]
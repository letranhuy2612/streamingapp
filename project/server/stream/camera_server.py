import os
import cv2
from project.server.stream.stream import BaseCamera
import time
import imutils


class Camera(BaseCamera):
    video_source = 0

    def __init__(self,source):
        Camera.set_video_source(source)
        super(Camera, self).__init__()

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        try:
            camera = cv2.VideoCapture(Camera.video_source)
            fps = int(camera.get(cv2.CAP_PROP_FPS))
            print('FPS opencv:',fps)
            if not camera.isOpened():
                raise RuntimeError('Could not start camera.')
            while True:
                # read current frame
                _, img = camera.read()
                img = imutils.resize(img,width=640,height=640)
                # encode as a jpeg image and return it
                yield cv2.imencode('.jpg', img)[1].tobytes()
        except:
            print('Time End:',time.ctime(time.time()))
            print('Stop!!!!')
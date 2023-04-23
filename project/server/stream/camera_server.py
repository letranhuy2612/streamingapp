import os
import cv2
from project.server.stream.stream import BaseCamera


class Camera(BaseCamera):
    video_source = 0

    def __init__(self):
        Camera.set_video_source('D:/Workspace/Vehicle_detection/highway.mp4')
        super(Camera, self).__init__()

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera.video_source)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()

            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()
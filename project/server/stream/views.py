from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
import cv2
import time
from project.server import bcrypt, db
from project.server.models import User, BlacklistToken, Cameras

thread_cam_blueprint = Blueprint('thread_cam', __name__)

def gen(camera_stream, feed_type, topic):
    """Video streaming generator function."""
    unique_name = (feed_type, topic)

    num_frames = 0
    total_time = 0
    while True:
        time_start = time.time()

        cam_id, frame = camera_stream.get_frame(unique_name)
        if frame is None:
            break

        num_frames += 1

        time_now = time.time()
        total_time += time_now - time_start
        fps = num_frames / total_time
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# class DisplayAPI(MethodView):


from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
import cv2
import time
from project.server import bcrypt, db
from project.server.models import User, BlacklistToken, Cameras

thread_cam_blueprint = Blueprint('thread_cam', __name__)

def gen(camera):
    """Video streaming generator function."""
    yield b'--frame\r\n'
    while True:
        frame = camera.get_frame()
        yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'



# class DisplayAPI(MethodView):


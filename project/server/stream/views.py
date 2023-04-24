from flask import Blueprint, request, make_response, jsonify,Response
from flask.views import MethodView
import cv2
import time
from project.server import bcrypt, db
from project.server.models import User, BlacklistToken, Cameras
from project.server.stream.camera_server import Camera
from kafka import KafkaConsumer
import json

thread_cam_blueprint = Blueprint('thread_cam', __name__)

def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        if frame is None:
            break
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

class GetcamAPI(MethodView):
    """
    Get subchanel and display
    """
    def get(self,camera_id):
        # get the auth token
        auth_token = request.headers.get('Authorization')
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                current_user = User.query.filter_by(id=resp).first()
                cam = Cameras.query.filter_by(user_id=current_user.id,id = camera_id).first()
                if cam.sub_chanel == True:
                    rtsp_path = f"rtsp://{cam.name}:{cam.password}@{cam.address}:{cam.port}/"
                    return Response(gen(Camera(source=rtsp_path)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 401        
class GetdataAPI(MethodView):
    def get(self):
        auth_token = request.headers.get('Authorization')
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                current_user = User.query.filter_by(id=resp).first()
                consumer = KafkaConsumer(
                    'testing',
                    bootstrap_servers='localhost:9092',
                    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
                )
                for message in consumer:
                    message = message.value
                    print('------------------------------------------------------------')
                    print(message)        

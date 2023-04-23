
import cv2
from flask import Flask, render_template, Response
from threading import get_ident
import time
import threading

class CameraEvent:
    """thông báo cho tất cả các client đang kết nối khi có một khung hình mới."""
    def __init__(self):
        self.events = {}

    def wait(self):
        """Được gọi từ mỗi luồng client để đợi khung hình mới nhất."""
        ident = get_ident()
        if ident not in self.events:
            # Đây là client mới
            # Thêm một mục cho client mới vào từ điển self.events
            # Mỗi mục gồm hai phần tử, một là threading.Event() và thời điểm timestamp
            self.events[ident] = [threading.Event(), time.time()]
        return self.events[ident][0].wait()

    def set(self):
        """Được gọi bởi luồng camera khi có một khung hình mới được cung cấp."""
        now = time.time()
        remove = None
        for ident, event in self.events.items():
            if not event[0].isSet():
                # Nếu event của client này chưa được set, thì set nó
                # Cập nhật thời điểm timestamp mới nhất thành hiện tại
                event[0].set()
                event[1] = now
            else:
                # Nếu event của client này đã được set, điều đó có nghĩa là client
                # chưa xử lý khung hình trước đó
                # Nếu event đã được set trong quá trình quá 5 giây, hãy xem như
                # client đã bị ngắt kết nối và loại bỏ nó ra khỏi danh sách
                if now - event[1] > 5000:
                    remove = ident
        if remove:
            del self.events[remove]

    def clear(self):
        """Được gọi từ mỗi luồng client sau khi đã xử lý một khung hình."""
        self.events[get_ident()][0].clear()
        
class BaseCamera(object):
	thread = None  # background thread that reads frames from camera
	frame = None  # current frame is stored here by background thread
	last_access = 0  # time of last client access to the camera
	event = CameraEvent()

	def __init__(self):
		"""Start the background camera thread if it isn't running yet."""
		if BaseCamera.thread is None:
			BaseCamera.last_access = time.time()

			# start background frame thread
			BaseCamera.thread = threading.Thread(target=self._thread)
			BaseCamera.thread.start()

			# wait until first frame is available
			BaseCamera.event.wait()

	def get_frame(self):
		"""Return the current camera frame."""
		BaseCamera.last_access = time.time()

		# wait for a signal from the camera thread
		BaseCamera.event.wait()
		BaseCamera.event.clear()

		return BaseCamera.frame

	@staticmethod
	def frames():
		""""Generator that returns frames from the camera."""
		raise RuntimeError('Must be implemented by subclasses.')

	@classmethod
	def _thread(cls):
		"""Camera background thread."""
		print('Starting camera thread.')
		print('timestart:',time.time())
		frames_iterator = cls.frames()
		try:
			for frame in frames_iterator:
				BaseCamera.frame = frame
				BaseCamera.event.set()  # send signal to clients
				time.sleep(0)

				# if there hasn't been any clients asking for frames in
				# the last 10 seconds then stop the thread
				if time.time() - BaseCamera.last_access > 10:
					frames_iterator.close()
					print('Stopping camera thread due to inactivity.')
					break
			BaseCamera.thread = None
		except:
			print("vào day:",time.time())            
			exit
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
        fps = int(camera.get(cv2.CAP_PROP_FPS))
        print(fps)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()
            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()

app = Flask(__name__)


@app.route('/')
def index():
    """Video streaming home page."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        if frame is None:
            break
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# @app.route('/video_feed')
# def video_feed():
#     """Video streaming route. Put this in the src attribute of an img tag."""
#     return Response(gen(Camera()),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(threaded=True)
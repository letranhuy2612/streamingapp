import time
import cv2
from kafka import KafkaProducer
from imutils.video import VideoStream

topic = "0"
REMOVE_LOGS = False


def publish_camera(PATH):
    """
    Publish camera video stream to specified Kafka topic.
    Kafka Server is expected to be running on the localhost. Not partitioned.
    """

    # Start up producer
    producer = KafkaProducer(bootstrap_servers='localhost:9092')

    cap = VideoStream(PATH)
    stream = cap.start()
    i = 0
    t1 = time.time()
    try:
        while True:
            frame = stream.read()
            frame = cv2.resize(frame, (480, 480), 
                               interpolation=cv2.INTER_AREA)

            ret, buffer = cv2.imencode('.jpg', frame)
            i += 1
            if i % 1000 == 0:
                print("SEND", i, time.time() - t1)
                t1 = time.time()
            if i % 10 in [0, 1]:
                continue
            producer.send(topic, buffer.tobytes())

            # Choppier stream, reduced load on processor
            # time.sleep(0.2)

    except:
        print("\nExiting.")
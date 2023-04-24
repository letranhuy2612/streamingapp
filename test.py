from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'testing',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)
for message in consumer:
    message = message.value
    print('---------------------------------------')
    print(message)


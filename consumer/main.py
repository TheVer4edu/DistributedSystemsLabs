import sys
import pika
import requests
import json
from os import getenv


USER = getenv("RABBITMQ_DEFAULT_USER") or "postrgres"
PASSWORD = getenv("RABBITMQ_DEFAULT_PASS") or "password"
BROKER_HOSTNAME = 'rabbit'
WEB_HOSTNAME = 'balancer'
WEB_PORT = '80'


CONNECTION_URL = f'amqp://{USER}:{PASSWORD}@{BROKER_HOSTNAME}:5672/%2F'

QUEUE_NAME = 'links'


def handle_message(ch, method, properties, body):
    body_str = body.decode('utf-8')
    link_json = json.loads(body_str)
    response = requests.get(link_json['url'], timeout=10)
    status = response.status_code
    payload = {'id': int(link_json['id']), 'status': str(status)}
    payload_json = json.dumps(payload)
    result = requests.put(f'http://{WEB_HOSTNAME}:{WEB_PORT}/links/', data=payload_json)
    print(result.content)


def main():
    connection = pika.BlockingConnection(pika.URLParameters(CONNECTION_URL))
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME)
    channel.basic_consume(queue=QUEUE_NAME, auto_ack=True, on_message_callback=handle_message)
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        sys.exit(0)

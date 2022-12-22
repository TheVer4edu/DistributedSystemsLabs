import sys
from typing import Optional

import pika
import requests
import json
from os import getenv

import redis

USER = getenv("RABBITMQ_DEFAULT_USER") or "postrgres"
PASSWORD = getenv("RABBITMQ_DEFAULT_PASS") or "password"
BROKER_HOSTNAME = 'rabbit'
WEB_HOSTNAME = 'balancer'
WEB_PORT = '80'

CACHE_HOSTNAME = 'cache'
CACHE_PORT = '6379'

CONNECTION_URL = f'amqp://{USER}:{PASSWORD}@{BROKER_HOSTNAME}:5672/%2F'

QUEUE_NAME = 'links'

redis_cache = redis.Redis(host=CACHE_HOSTNAME, port=int(CACHE_PORT), db=0)


def get_link_status(link: str) -> str:
    key = f"url-{link}"
    status = get_status_from_cache(key)
    if status is None:
        status = fetch_status_from_inet(link)
        update_status_in_cache(key, status)
    return status


def get_status_from_cache(key: str) -> Optional[str]:
    value = redis_cache.get(key)
    return None if value is None else value.decode("utf-8")


def update_status_in_cache(key: str, status_code: str) -> None:
    redis_cache.set(name=key, value=status_code)


def fetch_status_from_inet(link: str) -> str:
    response = requests.get(link, timeout=10)
    status = str(response.status_code)
    return status


def handle_message(ch, method, properties, body):
    body_str = body.decode('utf-8')
    link_json = json.loads(body_str)
    status = get_link_status(link_json['url'])
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

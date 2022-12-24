import json
import os
import sys
import uuid
from os import getenv
from typing import Optional, List
from os.path import exists

import nltk
import pika
import redis
import requests
from nltk.corpus import stopwords
from sumy.models.dom import Sentence
from sumy.nlp.stemmers import Stemmer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.html import HtmlParser
from sumy.summarizers.lsa import LsaSummarizer as Summarizer

nltk.download('punkt')
nltk.download('stopwords')

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

LANGUAGE = "russian"
SENTENCES_COUNT = 10

BOT_TOKEN = '5787993542:AAETVt3Zk88jim0GAEWJJkSLirvrzz9n1MI'


def get_link_status(link: str) -> str:
    key = f"url-{link}"
    status = get_status_from_cache(key)
    if status is None:
        status = fetch_summarization(link)
        update_status_in_cache(key, status)
    return status


def get_status_from_cache(key: str) -> Optional[str]:
    value = redis_cache.get(key)
    return None if value is None else value.decode("utf-8")


def update_status_in_cache(key: str, status_code: str) -> None:
    redis_cache.set(name=key, value=status_code)


def create_resources_if_not_exists(filename):
    path = filename.split('/')
    for i in range(2, len(path) + 1):
        path_element = '/'.join(path[0:i])
        if not exists(path_element):
            if path_element.lower().endswith(('.txt',)):
                f = open(path_element, 'x')
                f.close()
            else:
                os.mkdir(path_element)


def fetch_summarization(link: str) -> str:
    parser = HtmlParser.from_url(link, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)
    summarizer = Summarizer(stemmer)
    summarizer.stop_words = set(stopwords.words(LANGUAGE))
    sentences: List[Sentence] = [sentence for sentence in summarizer(parser.document, SENTENCES_COUNT)]
    sentences = [sentence._text for sentence in sentences]
    generated_filename = uuid.uuid4().hex
    result_filename = f'static/results/{generated_filename}.txt'
    volume_filename = f'/appdata/results/{generated_filename}.txt'
    create_resources_if_not_exists(volume_filename)
    with open(volume_filename, 'w') as fp:
        fp.writelines(sentences)
        fp.close()
    return result_filename


def handle_message(ch, method, properties, body):
    body_str = body.decode('utf-8')
    link_json = json.loads(body_str)
    tg_id = link_json['tg_uid']
    status = get_link_status(link_json['url'])
    payload = {'id': int(link_json['id']), 'result_url': str(status)}
    payload_json = json.dumps(payload)
    requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={tg_id}&text=Краткий пересказ составлен: Скачать - http://summarizer.ru/api/{status}')
    result = requests.put(f'http://{WEB_HOSTNAME}:{WEB_PORT}/api/links/', data=payload_json)
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

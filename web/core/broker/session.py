import pika

CONNECTION_URL = 'amqp://rabbituser:password@rabbit:5672/%2F'

QUEUE_NAME = 'links'

# channel.queue_declare(queue=QUEUE_NAME)


def publish_task(task: str):
    connection = pika.BlockingConnection(pika.URLParameters(CONNECTION_URL))
    channel = connection.channel()
    channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=task.encode('utf-8'))
    channel.close()
    connection.close()
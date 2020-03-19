import json
import os
from threading import Thread

import pika
import uuid


class ClassifierClient(object):

    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=os.environ.get('RABBIT_HOST', 'localhost')))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, uid):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=uid)
        while self.response is None:
            self.connection.process_data_events()
        resp = json.loads(self.response)
        with open(os.path.join('data', uid + '.json'), 'w') as f:
            json.dump(resp, f)

    def call_async(self, uid):
        Thread(target=self.call, args=(uid, )).start()


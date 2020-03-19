import os
import shutil
import tempfile
from time import sleep

import pika
import json
import pytesseract
import requests
import torch

from transformers import *


def perform_ocr(uid):
    ui_host = os.environ.get('UI_HOST', 'http://localhost:5000')
    tfn = os.path.join(tempfile.gettempdir(), uid + '.jpg')
    resp = requests.get(ui_host + '/serve/' + uid, stream=True)
    with open(tfn, 'wb') as f:
        shutil.copyfileobj(resp.raw, f)
    tess_output = pytesseract.image_to_string(tfn, lang='eng', config="--psm 3 --oem 1")
    return tess_output


@torch.no_grad()
def classify(text):
    if not hasattr(classify, 'model'):
        classify.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        classify.model = BertForSequenceClassification.from_pretrained('./model')
        classify.model.eval()

    tokenizer = classify.tokenizer
    model = classify.model

    tokens = tokenizer.encode(text, max_length=256, pad_to_max_length=True)
    tokens = torch.tensor([tokens])

    _logits = model(tokens)[0]
    _scores = torch.softmax(_logits, dim=-1)[0]

    _labels = [(model.config.id2label[i], _scores[i].item()) for i in range(len(_scores))]
    _labels.sort(key=lambda k: -k[1])

    return _labels


def on_request(ch, method, props, body):
    uid = body.decode()
    print('Processing:', uid)
    text = perform_ocr(uid)
    cls = classify(text)
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id=props.correlation_id),
                     body=json.dumps(cls))
    ch.basic_ack(delivery_tag=method.delivery_tag)


sleep(10)  # wait for rabbit to start
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=os.environ.get('RABBIT_HOST', 'localhost')))

channel = connection.channel()
channel.queue_declare(queue='rpc_queue')


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)

channel.start_consuming()

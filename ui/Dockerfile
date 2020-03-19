FROM python:3.7
ADD requirements.txt /tmp
WORKDIR /tmp
RUN pip install -r requirements.txt
ADD . /app
WORKDIR /app
CMD gunicorn --bind=0.0.0.0:8080 main:app

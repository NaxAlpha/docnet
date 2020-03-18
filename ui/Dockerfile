FROM python:3.7
ADD requirements.txt /tmp
WORKDIR /tmp
RUN pip install -r requirements.txt -f https://download.pytorch.org/whl/torch_stable.html
ADD . /app
WORKDIR /app
CMD uvicorn --host=0.0.0.0 port=8080 main:app

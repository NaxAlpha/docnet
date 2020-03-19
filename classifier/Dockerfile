FROM python:3.7
RUN apt update && apt -y install tesseract-ocr
ADD requirements.txt /tmp
WORKDIR /tmp
RUN pip install -r requirements.txt -f https://download.pytorch.org/whl/torch_stable.html
ADD . /app
WORKDIR /app
CMD python app.py


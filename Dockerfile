FROM python:3.11.3

WORKDIR /app

COPY . /app/

RUN pip install -requirements.txt

CMD ["python3", "app.py"]
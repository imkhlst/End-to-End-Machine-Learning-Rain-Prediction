FROM python:3.11-slim-buster

WORKDIR /app

COPY . /app/

# Upgrade pip first
RUN pip install --upgrade pip

# Install numpy first and pin it BEFORE installing others
RUN pip install "numpy<2.0"

# Then install other dependencies (avoid upgrading numpy again)
RUN pip install -r requirements.txt

RUN pip install --no-cache-dir --force-reinstall "numpy==1.26.4"

CMD ["python3", "app.py"]
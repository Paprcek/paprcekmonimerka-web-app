FROM python:3.11-slim

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app/

CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:5001", "app:app"]

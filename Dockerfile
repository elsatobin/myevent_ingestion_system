FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY stream_server.py ./
COPY wait-for-it.sh ./

ENV PYTHONPATH=/app

CMD ["./wait-for-it.sh", "my-postgres:5432", "--", "python", "stream_server.py"]
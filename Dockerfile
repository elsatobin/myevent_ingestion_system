# app/Dockerfile
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 복사
COPY ./app ./app

# 포트 설정
EXPOSE 8000

# uvicorn 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
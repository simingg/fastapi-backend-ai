# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 8080
ENV PORT=8080

CMD ["uvicorn", "application:application", "--host", "0.0.0.0", "--port", "8080"]
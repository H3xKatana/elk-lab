FROM python:3.11-slim

WORKDIR /app

COPY app.py .

RUN mkdir -p /var/log/app

EXPOSE 5000

CMD ["python", "app.py"]

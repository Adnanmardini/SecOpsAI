FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install kafka-python loguru python-dotenv psycopg2-binary
CMD ["python3", "alert_consumer.py"]

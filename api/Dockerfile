FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install fastapi uvicorn slowapi python-jose[cryptography] passlib[bcrypt] kafka-python
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

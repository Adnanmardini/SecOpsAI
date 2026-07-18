FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip setuptools wheel && \
    pip install \
        fastapi \
        uvicorn \
        slowapi \
        numpy \
        scikit-learn \
        xgboost \
        joblib \
        psycopg2-binary \
        bcrypt \
        passlib \
        cryptography \
        ecdsa \
        rsa \
        python-jose==3.3.0
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

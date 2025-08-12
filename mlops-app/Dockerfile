FROM python:3.11-slim

WORKDIR /app

COPY mlops-app/app/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY mlops-app/app ./app
COPY mlops-app/model ./model

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

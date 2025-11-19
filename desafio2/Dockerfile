FROM python:3.11-slim

WORKDIR /app

RUN pip install psycopg2-binary

COPY app/headphones_catalog.py .

CMD ["python", "headphones_catalog.py"]

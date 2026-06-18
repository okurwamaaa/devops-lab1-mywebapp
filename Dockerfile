FROM python:3.12-slim

WORKDIR /opt/mywebapp

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5200

CMD ["sh", "-c", "python3 migrate.py && python3 app.py"]
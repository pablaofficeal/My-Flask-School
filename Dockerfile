FROM ubuntu:22.04 AS base

ARG TZ=UTC
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    ca-certificates \
    tzdata \
    build-essential \
    gcc \
    libssl-dev \
    libffi-dev \
    libpq-dev \
    curl \
    git \
 && ln -fs /usr/share/zoneinfo/$TZ /etc/localtime \
 && dpkg-reconfigure -f noninteractive tzdata || true \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# non-root app user and app directory
RUN groupadd -r app \
 && useradd -r -g app -m -d /home/app -s /usr/sbin/nologin app \
 && mkdir -p /app \
 && chown -R app:app /app

WORKDIR /app

FROM python:3.12.9

WORKDIR /app

COPY . .

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "backend/app.py"]

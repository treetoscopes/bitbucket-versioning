# Use the official Python image from the Docker Hub
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg \
    software-properties-common \
    git \
    curl \
    wget \
    sudo \
    openssh-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
       
        
        
RUN pip install poetry
RUN poetry config virtualenvs.create false

COPY . .

RUN poetry install

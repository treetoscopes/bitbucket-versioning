# Use the official Python image from the Docker Hub
FROM python:3.12-alpine

RUN apk update && apk add --no-cache \
        git \
        sudo \
        openssh-client
        
RUN pip install poetry
RUN poetry config virtualenvs.create false

COPY . .

RUN poetry install

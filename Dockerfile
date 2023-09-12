FROM python:3.9.18-slim

SHELL ["/bin/bash", "-c"]

USER root

WORKDIR /root

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py main.py

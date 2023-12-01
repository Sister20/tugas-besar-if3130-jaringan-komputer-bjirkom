FROM python:3.11-alpine

WORKDIR /usr/src/app

RUN pip install psycopg2-binary

COPY . .
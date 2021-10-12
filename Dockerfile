FROM python:3.7-alpine

WORKDIR /home/app

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN apk update
RUN apk add postgresql-dev gcc python3-dev musl-dev
RUN apk add --update g++
COPY ./app/requirements.txt /home/app/requirements.txt
RUN pip install -r requirements.txt
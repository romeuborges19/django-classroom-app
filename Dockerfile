FROM python:3.11

ENV PYTHONUNBUFFERED 1

RUN mkdir /django-classroom-app

WORKDIR /django-classroom-app

ADD . /django-classroom-app/

RUN pip install -r requirements.txt

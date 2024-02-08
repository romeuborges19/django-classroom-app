FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get install libpq-dev

RUN mkdir /django-classroom-app

WORKDIR /django-classroom-app

ADD . /django-classroom-app/

COPY ./classroom/api/credentials.json /django-classroom-app/classroom/api/credentials.json

RUN pip install -r requirements.txt

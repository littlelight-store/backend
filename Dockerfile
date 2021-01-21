FROM python:3.8-alpine

RUN mkdir /opt/app
WORKDIR /opt/app


RUN apk update && apk upgrade && apk add --no-cache --virtual .build-deps \
    postgresql-dev gcc python3-dev musl-dev zlib-dev \
    jpeg-dev build-base

ENV PYTHONUNBUFFERED 1

ADD requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python3", "./src/manage.py", "runserver", "0.0.0.0:8000"]

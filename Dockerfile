FROM python:3.9.13-alpine
WORKDIR /project

ADD . /project
ADD ./upload/avatar/default.jpg upload/avatar/

RUN apk add --update --no-cache build-base libpq-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del build-base --purge && \
    chmod +x ./startup.sh
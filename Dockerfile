FROM python:3.9.15-alpine
WORKDIR /project

ADD . /project

RUN mkdir -p /etc/default && \
    addgroup celery && adduser celery -G celery -s /bin/sh -D && \
    mkdir -p /var/log/celery/ && chown celery:celery /var/log/celery/ && \
    mkdir -p /var/run/celery/ && chown celery:celery /var/run/celery/

COPY ./celeryd /etc/init.d/celeryd
COPY ./celeryd.conf /etc/default/celeryd

RUN apk add --update --no-cache build-base libpq-dev openrc jpeg-dev \
                                                            zlib-dev \
                                                            freetype-dev \
                                                            lcms2-dev \
                                                            openjpeg-dev \
                                                            tiff-dev \
                                                            tk-dev \
                                                            tcl-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    chmod +x /etc/init.d/celeryd && chmod +x ./startup.sh

ENTRYPOINT ["./startup.sh"]

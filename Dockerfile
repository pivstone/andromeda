FROM alpine:3.4

MAINTAINER PivStone<PivStone@gmail.com>

EXPOSE 5511

ENV APP_HOME /srv/andromeda
ENV DJANGO_SETTINGS_MODULE andromeda.settings.prodn

COPY . ${APP_HOME}
VOLUME ${APP_HOME}/etc
VOLUME ${APP_HOME}/data
WORKDIR ${APP_HOME}


RUN apk update
RUN apk add nginx git bash \
    && apk add openssl libc-dev python3-dev gcc \
    && rm -rf /var/cache/apk/*

COPY etc/andromeda.nginx.conf /etc/nginx/server/
COPY etc/alpine.nginx.conf /etc/nginx

RUN pip3 install -r requirements/production.txt -U
CMD ["entrypoint.sh"]

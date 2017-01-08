#!/bin/sh
mkdir -p /run/nginx
/usr/sbin/nginx -c /etc/nginx/alpine.nginx.conf
cd /srv/andromeda
gunicorn andromeda.wsgi -w 8 -b 0.0.0.0:5510 --access-logfile=/srv/andromeda/logs/andromeda.access.log

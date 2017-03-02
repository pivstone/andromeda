
# Docker Registry V2 Python Version

[![Python Support Status](https://img.shields.io/badge/python-3.4%2C%203.5%2C%20pypy-blue.svg)]()
[![Build Status](https://travis-ci.org/pivstone/andromeda.svg?branch=master)](https://travis-ci.org/pivstone/andromeda)
[![Coverage Status](https://coveralls.io/repos/github/pivstone/andromeda/badge.svg?branch=master)](https://coveralls.io/github/pivstone/andromeda?branch=master)

An unofficial docker distribution project.


# Stage
!Beta

# Dependency:
* Python 3
* Django
* Django Rest Framework
* ecdsa
* Nginx


# Install

1. rename configuration file
 
	> mv /path/to/andromeda/etc/andromeda.ini.example  /path/to/andromeda/etc/andromeda.ini
 
 
2. modify configuration file

	```ini
	[storage]
	repo_dir=tmp/v2/repo  # reposities storage path
	blob_dir=tmp/v2/blob  # blob storage path
	
	
	
	[email]    # Report Email Settings
	host = smtp.xxx.com
	port = 465
	user = django@xxx.com
	password = password
	subject_prefix = '[django-andromeda]'
	```

3. rename django SECRET KEY file

	> mv /path/to/andromeda/etc/key.txt.example /path/to/andromeda/etc/key.txt
 
4. generate a SECRET KEY for django

	see [django SECRET_KEY](https://docs.djangoproject.com/en/1.10/ref/settings/#std:setting-SECRET_KEY)

5. install dependency

	Recommend using [virtualenv](https://pypi.python.org/pypi/virtualenv) to isolate your Python dependency environment,

	> pip install -r requirements/prodn.txt

6. modify nginx config file

	reference: /path/to/andromeda/etc/nginx.conf

# docker-compose.yml 

```yml
version: "2"
services:
  app:
    image:  pivstone/andromeda:latest
    volumes:
      - /srv/andromeda/etc:/srv/andromeda/etc
      - /srv/andromeda/logs:/srv/andromeda/logs
      - /srv/andromeda/data:/srv/andromeda/data
    ports:
      - 5511:5511
    working_dir: /srv/andromeda
    restart: always
```

# Run

* Dev Environment 

	Please use `runserver`，if just use it in developmenent environment,

	> python manage.py runserver 

* Production Environment

	Recommend using [Gunicorn](http://gunicorn.org) as a web container for django ,[why not use runserver in prodoction environment](https://docs.djangoproject.com/en/1.10/ref/django-admin/#runserver)

	> gunicorn andromeda.wsgi -w 8 -b 0.0.0.0:8000
 

# Test Unit

	install tox

	> tox

## Nginx Configuration：

```conf
worker_processes auto;

events {
  worker_connections 1024;
  use epoll;
  multi_accept on;
}

server {
    listen 80 ;

    client_max_body_size 0;
    tcp_nodelay on;

    location /v2 {
       proxy_http_version 1.1;   # 强制 1.1
       proxy_pass http://127.0.0.1:8000; # 后端接口
       proxy_set_header        X-Real-IP $remote_addr;
       proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header        Host $http_host;
       proxy_request_buffering on;
       chunked_transfer_encoding on;  # 让 Nginx 处理 Chunked 请求

    }

    location /download/blobs {
       alias /Users/andromeda/tmp/v2/blob;   # Blobs 文件地址
       expires 1d;  # Blobs 内容级别不变，可以考虑半永久缓存
    }

}
```


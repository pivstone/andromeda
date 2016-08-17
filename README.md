
# Docker Distribution Python Version (unofficially) 

A unofficially docker distribution projects.

# Stage
!Beta

# Dependency:
* Python 3
* Django
* Django Restful Framework
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

3. rename django secret key file

	> mv /path/to/andromeda/etc/key.txt.example /path/to/andromeda/etc/key.txt
 
4. generate a secret key for django

	see [django SECRET_KEY](https://docs.djangoproject.com/en/1.10/ref/settings/#std:setting-SECRET_KEY)

5. install dependency

	Recommend use [virtualenv](https://pypi.python.org/pypi/virtualenv) to isolate your Python dependency environment,

	> pip install -r requirements/prodn.txt

6. modify nginx config file

	reference: /path/to/andromeda/etc/nginx.conf


# Run

* Dev Environment 

	if just use in dev env,use `runserver`

	> python manage.py runserver 

* Production Environment

	Recommend use [Gunicorn](http://gunicorn.org) as a web container for django ,[why not use runserver in prodoction environment](https://docs.djangoproject.com/en/1.10/ref/django-admin/#runserver)

	> gunicorn andromeda.wsgi -w 8 -b 0.0.0.0:8000
 

# Test Unit

	install tox

	> tox

## Nginx 配置说明：

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
       alias /Users/pivstone/workspace/***REMOVED***/andromeda/tmp/v2/blob;   # Blobs 文件地址
       expires 1d;  # Blobs 内容级别不变，可以考虑半永久缓存
    }

}
```

==Note== 由于需要 Nginx 在前端，拼接好 Chunked 请求的所有内容，所以Nginx 前端机可以有一定的内存要求


## Roadmap
* Web Hook
* Upload Temp Blob GC
* Auth?

## Some Else:

Blobs 的 GC，Docker 官方短期内也不支持， 本质原因是 Docker Distribution 设计的时候，无状态化处理、分布式改造都是依赖于 Storage，如果 Storage 是分布式的，每一个独立的 Registry 就天然的满足分布式的情况，但当需要对于无用的 Blobs 回收的情况下，Docker 官方就无能为力，这个是 Storage 层的领域。

Blobs 的回收的困难原因是，Docker Distribution 在存储 Layers 的时候会通过 Layers 的 SHA256 的值来去除检查（理论上 SHA256 是唯一的），如果一个 Layers SHA 的值对应的文件存在在 Registry 上则 Docker Client 就不会重新上传这个文件了。但要删除一个 Blobs 的时候就出现了问题，什么时候这个Blobs 才是不再需要的，假如节点 A 发现 Blobs 无效了，准备删除，节点 B 上传的 Image 需要这个 Blobs，就会出现 Blobs 丢失问题。

但不会收回 Blobs 的话 ，会导致 Blobs 仓库越来越大。

官方给出的意见：
1 使用引用计算器，但需要 Paxos 、Raft 之类的算法处理一致性和分布式锁的问题。相当复杂（还有一个 Docker 不想让 Registry 之间有通信，这样会让整个 System 变得复杂，难以维护）
2 使用中心化数据库，使用数据库的事务来处理这个问题，（个人以为：Docker 不用这个是因为不想引入数据库，也不想使用文件系统以为的数据库）
3 使用 World GC，即暂停所有的上传业务，来回收资源（如果可以像 12306 那样下限维护就好说）




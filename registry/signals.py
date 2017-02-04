# coding=utf-8
from django.dispatch import Signal

__author__ = 'pivstone'

blob_upload_init = Signal(providing_args=['name', 'uuid'])  # 用户开始上传新的blob
blob_upload_complete = Signal(providing_args=['name', 'uuid', 'digest'])  # 用户开始上传完成blob
manifest_save = Signal(providing_args=['name', 'reference'])  # 用户新建 manifest
manifest_delete = Signal(providing_args=['name', 'reference'])  # 用户删除 manifest

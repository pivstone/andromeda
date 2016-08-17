from __future__ import unicode_literals
import json
from collections import OrderedDict
from django.utils import six
from registry import EMPTY_BLOB_DIGEST, exceptions, crypto, CONFIG_TYPE, LAYER_TYPE, signals
from registry.storages import storage

from hashlib import sha256

__author__ = 'pivstone'


def digest_verify(digest, size):
    """
    Docker Manifest Schema V2 2 版本的 digest 校验
    :param digest:
    :param size:
    :return:
    """
    blob_length = storage.get_blob_length(digest)
    if not blob_length:
        raise exceptions.BlobUnknownException(detail={"digest": digest})
    if size != blob_length:
        raise exceptions.ManifestUnverifiedException()


class AbstractManifest(object):
    def __init__(self, data, name, reference):
        self.data = data
        self.name = name
        self.reference = reference
        self.verify()

    @property
    def layers(self):
        """
        获取 Manifest 所有 Layers 的digest
        :return:
        """
        raise NotImplementedError()

    def verify(self):
        """
        Manifest 校验
        :return:
        """
        raise NotImplemented()

    def convert(self):
        raise NotImplemented()

    def save(self):
        """
        保存 manifest 文件
        并做 相关 Layers 的Links 操作
        :return:
        """
        data_string = json.dumps(self.data, indent=4).encode("utf-8")
        if not isinstance(data_string, six.binary_type):
            data_string = data_string.encode("utf-8")
        manifest_digest = storage.save_manifest(data_string)
        # save tags
        current_tag_path = storage.get_tag_current_path(name=self.name, tag_name=self.reference)
        storage.link(manifest_digest, current_tag_path)
        tag_index_path = storage.get_tag_index_path(name=self.name, tag_name=self.reference, digest=manifest_digest)
        storage.link(manifest_digest, tag_index_path)

        # Save reference
        reference_path = storage.get_reference_path(name=self.name, digest=manifest_digest)
        storage.link(manifest_digest, reference_path)

        for layer in self.layers:
            layer_path = storage.get_layer_path(name=self.name, digest=layer)
            storage.link(layer, layer_path)


class ManifestV2(AbstractManifest):
    """
    Schema V2 第二版 Manifest
    """

    def verify(self):
        config = self.data['config']
        digest_verify(config['digest'], config['size'])
        if config['mediaType'] != CONFIG_TYPE:
            raise exceptions.ManifestInvalidException(detail={"config": "mediaType invalid"})
        for layer in self.data['layers']:
            if layer['mediaType'] != LAYER_TYPE:
                raise exceptions.ManifestInvalidException()
            digest_verify(layer['digest'], layer['size'])

    @property
    def layers(self):
        return [layer["digest"] for layer in self.data['layers']]

    def convert(self):
        """
        第二版转化成第一版
        """
        data = OrderedDict()
        data["schemaVersion"] = 1
        data["name"] = self.name
        data["tag"] = self.reference
        config_digest = self.data['config']['digest']
        config_data = json.loads(storage.get_blob(config_digest))
        data['architecture'] = config_data['architecture']
        fs_layers = list()
        history = list()
        data['fsLayers'] = fs_layers
        data['history'] = history
        layer_count = 0
        parent_id = ""

        for layer in config_data['history']:
            # 计算 blob
            h = sha256()
            empty = layer.get("empty_layer", False)
            if empty:
                blob_sum = EMPTY_BLOB_DIGEST
            else:
                blob_sum = self.data['layers'][layer_count]['digest']
                layer_count += 1
            fs_layers.append({"blobSum": blob_sum})

            # 构建 v1Compatibility 内容
            h.update(blob_sum.encode() + b"  " + parent_id.encode())
            v1_id = h.digest().hex()
            v1_layers = OrderedDict()
            v1_layers["id"] = v1_id
            v1_layers["created"] = layer['created']
            v1_layers["container_config"] = layer['created_by']
            if parent_id:
                v1_layers['parent'] = parent_id
            for k in ("author", "comment", "throwaway"):
                if k in layer:
                    v1_layers[k] = layer[k]
            history.append({"v1Compatibility": json.dumps(v1_layers)})
            parent_id = v1_id
        data['history'] = history.reverse()
        return crypto.jws_sign(data)


class ManifestV1(AbstractManifest):
    """
    Schema V2 第一版 Manifest， 带 JWS 的版本
    """

    def verify(self):
        for layer in self.data['fsLayers']:
            if not storage.get_blob_length(layer['blobSum']):
                raise exceptions.BlobUnknownException(detail={"digest": layer['blobSum']})

        v = crypto.Verifier(json.dumps(self.data))
        if not v.verify():
            raise exceptions.ManifestUnverifiedException()

    @property
    def layers(self):
        return [layer["blobSum"] for layer in self.data['fsLayers']]

    def convert(self):
        return self.data


class Manifest(object):
    def __init__(self, data, name, reference):
        self.name = name
        self.reference = reference
        self.version = data['schemaVersion']
        if self.version == 2:
            self.manifest = ManifestV2(data, name, reference)
        else:
            self.manifest = ManifestV1(data, name, reference)

    def save(self):
        self.manifest.save()
        signals.manifest_save.send(sender=self.__class__, name=self.name, reference=self.reference)

    def get_v1_manifest(self):
        return self.manifest.convert()

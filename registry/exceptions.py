__author__ = 'pivstone'


class RegistryException(Exception):
    code = "UNKNOWN"
    message = "unknown"
    status = 400
    detail = {}

    def __init__(self, detail=None):
        self.detail = detail or {}

    def errors(self):
        return {"errors": [{"code": self.code, "message": self.message, "detail": self.detail}]}


class ManifestUnsupportedException(RegistryException):
    status = 415
    code = "MANIFEST UNSUPPORTED"
    message = "manifest unsupported"


class UnsupportedException(RegistryException):
    code = "UNSUPPORTED"
    message = "The operation is unsupported"


class BlobUploadInvalidException(RegistryException):
    code = "BLOB_UPLOAD_INVALID"
    message = "blob upload invalid"


class BlobDigestInvalidException(RegistryException):
    code = "BLOB_UPLOAD_INVALID"
    message = "digest did not match uploaded content"


class NameInvalidException(RegistryException):
    code = "NAME_INVALID"
    message = "invalid repository name"


class ManifestInvalidException(RegistryException):
    code = "MANIFEST_INVALID"
    message = "manifest invalid"


class ManifestUnverifiedException(RegistryException):
    code = "MANIFEST_UNVERIFIED"
    message = "manifest unverified"


class BlobUnknownException(RegistryException):
    code = "BLOB_UNKNOWN"
    message = "blob unknown to registry"


class BlobUploadUnknownException(RegistryException):
    code = "BLOB_UPLOAD_UNKNOWN"
    message = "blob upload unknown to registry"


class ManifestUnknownException(RegistryException):
    status = 404
    code = "MANIFEST_UNKNOWN"
    message = "manifest unknown"


class DockerDigestNotExistException(RegistryException):
    code = "DOCKER_DIGEST_HEADER_NOT_EXIST"
    message = "docker digest header not exist"


class DigestInvalidException(RegistryException):
    code = "DOCKER_DIGEST_INVALID"
    message = "docker digest invalid"

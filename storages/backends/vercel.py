import io
from typing import Literal
from tempfile import SpooledTemporaryFile

import requests
from storages.base import BaseStorage
from django.core.files.base import File
from django.core.exceptions import SuspiciousOperation, ImproperlyConfigured
from storages.utils import clean_name, safe_join
from vercel_storage import blob


class VercelStorageException(Exception):
    pass


class VercelStorageContent:
    url: str
    pathname: str
    size: int
    uploadedAt: str
    contentDisposition: str
    contentType: str

    def __init__(self, data_dict: dict):
        self.url = data_dict.get("url", "")
        self.pathname = data_dict.get("pathname", "")
        self.size = data_dict.get("size", 0)
        self.uploadedAt = data_dict.get("uploadedAt", "")
        self.contentDisposition = data_dict.get("contentDisposition", "")
        self.contentType = data_dict.get("contentType", "")


class VercelStorageResponseListdir:
    """
    exsample:
    {
        'hasMore': False,
        'blobs': [
            {
                'url': 'https://xlxsf7k5yyn6nuih.public.blob.vercel-storage.com/sample-CqB9mGLPfUrwFhlvvxySYXqZg7FrR5.txt',
                'pathname': 'sample.txt',
                'size': 6,
                'uploadedAt': '2024-05-18T04:00:05.633Z',
                'contentDisposition': 'attachment; filename="sample.txt"',
                'contentType': 'text/plain'
            },
            {
                'url': 'https://xlxsf7k5yyn6nuih.public.blob.vercel-storage.com/storage_save_test-ZSxwlZhXj7bmlZWCzGCMdOklAJEzHQ.png',
                'pathname': 'storage_save_test.png',
                'size': 311688,
                'uploadedAt': '2024-05-07T14:31:20.367Z',
                'contentDisposition': 'attachment; filename="storage_save_test.png"',
                'contentType': 'image/png'
            }
        ]
    }
    """

    hasMore: bool
    blobs: list[VercelStorageContent]

    def __init__(self, data_dict: dict):
        self.hasMore = data_dict.get("hasMore", False)
        self.blobs = [VercelStorageContent(blob) for blob in data_dict.get("blobs", [])]


class VercelStorage(BaseStorage):

    CHUNK_SIZE: int = 4 * 1024 * 1024

    def __init__(self, **settings):
        super().__init__(**settings)
        # Initialize connection settings for vercel-storage here
        self.client = blob
        self.options = settings
        self.options["token"] = blob.get_token(self.options)
        self.options["no_suffix"] = True

    def _save(self, name, content: File) -> str:
        # Save a file to Vercel storage
        name = self.get_available_name(name)
        if len(content) <= self.CHUNK_SIZE:
            self.client.put(name, content.read(), options=self.options)
        else:
            self._chunked_upload(content, name)
        return name

    def _chunked_upload(self, content: File, name: str) -> None:
        # Upload a file to Vercel storage in chunks
        raise NotImplementedError("Chunked upload is not supported")

    def _open(self, name, mode="rb"):
        # Open a file from Vercel storage
        return VercelStorageFile(name, mode, self)

    def listdir(self, path: str = "") -> VercelStorageResponseListdir:
        # List directories and files under a path in Vercel storage
        # DEFAULT_PAGE_SIZE = 100 (Depends on the vercel-storage library.)
        Warning(
            "Due to the dependency with `vercel-storage`, the `path` argument is ignored"
        )
        _data_dict = self.client.list(options=self.options)
        return VercelStorageResponseListdir(_data_dict)

    def exists(self, name: str) -> bool:
        # Check if a file exists in Vercel storage
        _list_content = self.listdir()
        _blobs = _list_content.blobs
        _dict_content = {content.pathname: content for content in _blobs}
        return name in _dict_content.keys()

    def get_content(self, name: str) -> VercelStorageContent:
        # Get the content of a file in Vercel storage
        _list_content = self.listdir()
        _blobs = _list_content.blobs
        _dict_content = {content.pathname: content for content in _blobs}
        if name not in _dict_content.keys():
            raise ImproperlyConfigured(f"File {name} does not exist")
        return _dict_content[name]

    def size(self, name: str) -> int:
        # Get the size of a file in Vercel storage
        content = self.get_content(name)
        return content.size

    def url(self, name: str) -> str:
        # Get the URL of a file in Vercel storage
        _content = self.get_content(name)
        return _content.url

    def delete(self, name) -> None:
        # Delete a file from Vercel storage
        _url = self.url(name)
        self.client.delete(_url, options=self.options)

    def get_byte(self, name) -> bytes:
        # Get the byte content of a file in Vercel storage
        url = self.url(name)
        _res = requests.get(url)
        if _res.status_code != 200:
            raise SuspiciousOperation(f"Failed to get blob for {name}")
        return _res.content


class VercelStorageFile(File):
    name: str
    size: int
    file: io.BytesIO
    closed: bool
    _mode: Literal["wb", "rb"]
    _is_dirty: bool
    _is_read: bool
    _storage: VercelStorage

    def __init__(
        self,
        name: str,
        mode: Literal["wb", "rb"],
        storage: VercelStorage,
        blob: bytes | None = None,
    ):
        self.name = name
        self._storage = storage
        self._mode = mode
        print("blob", blob)
        self.blob = self._storage.get_byte(name) if blob is None else blob
        self.size = len(self.blob)
        print("self.blob", self.blob)
        self.file = io.BytesIO(self.blob)

    def read(self, num_bytes=None):
        return self.file.read(num_bytes)

    def write(self, content):
        if "w" not in self.mode:
            raise AttributeError("File was opened for read-only access.")
        self.file = io.BytesIO(content)
        self._is_dirty = True
        self._is_read = True

    def open(self, mode=None):
        if not self.closed:
            self.seek(0)
        elif self.name and self._storage.exists(self.name):
            _file_blob = self._storage.get_byte(self.name)
            self.file = io.BytesIO(_file_blob)
            self._is_read = True
        else:
            raise ValueError("The file cannot be reopened.")

    def close(self):
        if self._is_dirty:
            self._storage._save(self.name, self)

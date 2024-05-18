from storages.base import BaseStorage
from django.core.files.base import File
from django.core.exceptions import SuspiciousOperation
from storages.utils import clean_name, safe_join
from .vercel_storage import blob

class VercelStorage(BaseStorage):
    def __init__(self, **settings):
        super().__init__(**settings)
        # Initialize connection settings for vercel-storage here
        # Example: self.client = VercelClient(self.settings)

    def _open(self, name, mode='rb'):
        # Open a file from Vercel storage
        return blob.open_blob(name, mode)

    def _save(self, name, content):
        # Save a file to Vercel storage
        return blob.save_blob(name, content)

    def delete(self, name):
        # Delete a file from Vercel storage
        blob.delete_blob(name)

    def exists(self, name):
        # Check if a file exists in Vercel storage
        return blob.blob_exists(name)

    def listdir(self, path):
        # List directories and files under a path in Vercel storage
        return blob.list_blobs(path)

    def size(self, name):
        # Get the size of a file in Vercel storage
        return blob.get_blob_size(name)

    def url(self, name):
        # Get the URL of a file in Vercel storage
        return blob.get_blob_url(name)

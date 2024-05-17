import unittest
from unittest.mock import patch, MagicMock

from storages.backends.vercel_storage import VercelStorage


class TestVercelStorage(unittest.TestCase):

    def setUp(self):
        self.storage = VercelStorage()

    @patch('storages.backends.vercel_storage.VercelStorage._open')
    def test_open(self, mock_open):
        name = 'test_open.txt'
        mode = 'rb'
        self.storage.open(name, mode)
        mock_open.assert_called_once_with(name, mode)

    @patch('storages.backends.vercel_storage.VercelStorage._save')
    def test_save(self, mock_save):
        name = 'test_save.txt'
        content = MagicMock()
        self.storage.save(name, content)
        mock_save.assert_called_once_with(name, content)

    @patch('storages.backends.vercel_storage.VercelStorage.delete')
    def test_delete(self, mock_delete):
        name = 'test_delete.txt'
        self.storage.delete(name)
        mock_delete.assert_called_once_with(name)

    @patch('storages.backends.vercel_storage.VercelStorage.exists')
    def test_exists(self, mock_exists):
        name = 'test_exists.txt'
        self.storage.exists(name)
        mock_exists.assert_called_once_with(name)

    @patch('storages.backends.vercel_storage.VercelStorage.listdir')
    def test_listdir(self, mock_listdir):
        path = 'test_path/'
        self.storage.listdir(path)
        mock_listdir.assert_called_once_with(path)

    @patch('storages.backends.vercel_storage.VercelStorage.size')
    def test_size(self, mock_size):
        name = 'test_size.txt'
        self.storage.size(name)
        mock_size.assert_called_once_with(name)

    @patch('storages.backends.vercel_storage.VercelStorage.url')
    def test_url(self, mock_url):
        name = 'test_url.txt'
        self.storage.url(name)
        mock_url.assert_called_once_with(name)


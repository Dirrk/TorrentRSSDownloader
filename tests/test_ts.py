__author__ = 'Dirrk'

import unittest

import app.TorrentDownloadService
import os


class TestTorrentService(unittest.TestCase):
    def test_create_folder(self):
        folder = "F:\\test-area\\test"
        folder1 = "F:\\test-area\\test\\create"
        folder2 = "F:\\test-area\\test\\create\\folder"

        if os.path.exists(folder2):
            os.rmdir(folder2)

        if os.path.exists(folder1):
            os.rmdir(folder1)

        if os.path.exists(folder):
            os.rmdir(folder)

        self.assertTrue(app.TorrentDownloadService.create_folder(folder))
        self.assertTrue(app.TorrentDownloadService.create_folder(folder2))
        self.assertTrue(os.path.exists(folder1))
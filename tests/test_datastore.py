__author__ = 'Dirrk'
import unittest

db_file = "C:\\Users\\derek_000\\PycharmProjects\\TorrentDownloader\\data\\database.db"
from lib.DataStore import DataStore


class TestDataStoreObject(unittest.TestCase):
    def setUp(self):
        self.db = DataStore(db_file)
        self.assertEqual(self.db.modified, 0)

    def test_load(self):
        self.db.load()
        self.assertGreater(self.db.modified, 0)
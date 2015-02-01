__author__ = 'Dirrk'
import unittest

db_file = "C:\\Users\\derek_000\\PycharmProjects\\TorrentDownloader\\data\\database.db"
import lib.DataStore as DataStoreLib


class TestDataStoreObject(unittest.TestCase):
    def setUp(self):
        db = DataStoreLib.DataStore(db_file)

    def test_get_modifiers(self):
        num = DataStoreLib.get_modifiers(db_file)
        self.assertEqual(num, 2)
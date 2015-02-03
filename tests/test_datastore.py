__author__ = 'Dirrk'
import unittest

from os import remove as rm
from os import path


db_file = "C:\\Users\\derek_000\\PycharmProjects\\TorrentDownloader\\data\\database.db"
db_test_file = "C:\\Users\\derek_000\\PycharmProjects\\TorrentDownloader\\data\\test_database.db"
from lib.DataStore import DataStore


class TestDataStoreObject(unittest.TestCase):
    def setUp(self):
        self.db = DataStore(db_file)
        self.assertEqual(self.db.modified, 0)

    def test_load(self):
        self.db.load()
        self.assertGreater(self.db.modified, 0)

    def test_create(self):
        db = DataStore(db_test_file)
        db.create()
        self.assertEqual(db.modified, 1)
        import sqlite3 as sql

        conn = sql.connect(db_test_file)

        for a in conn.execute('SELECT * FROM SETTINGS').fetchall():
            print "Found: ", a

        conn.close()

    @classmethod
    def tearDownClass(cls):
        if path.exists(db_test_file):
            rm(db_test_file)
__author__ = 'Dirrk'
import unittest

from os import remove as rm
from os import path
from app.rss.Feed import Feed
from app.rss.Subscription import Subscription
db_file = "C:\\Users\\derek_000\\PycharmProjects\\TorrentDownloader\\data\\database.db"
db_test_file = "C:\\Users\\derek_000\\PycharmProjects\\TorrentDownloader\\data\\test_database.db"
from lib.DataStore import DataStore


class TestDataStoreObject(unittest.TestCase):
    def setUp(self):
        self.db = DataStore(db_file)
        self.assertEqual(self.db.modified, 0)

        self.db_test = DataStore(db_test_file)
        self.db_test.create()

    def test_load(self):
        self.db.load()
        self.assertGreater(self.db.modified, 0)

    def test_create(self):
        self.assertEqual(self.db_test.modified, 1)
        import sqlite3 as sql

        conn = sql.connect(db_test_file)

        for a in conn.execute('SELECT * FROM SETTINGS').fetchall():
            self.assertGreater(int(a[1]), 0)
            print "Found: ", a

        conn.execute(
            '''
              INSERT INTO Feeds(url, name, frequency, last_pub) VALUES ("http://google.com", "Test_Google", 300, 0);
            '''
        )
        conn.execute(
            '''
              INSERT INTO Subscriptions(name, feedid) VALUES ('Test-Subscription', 1);
            '''
        )

        conn.commit()
        conn.close()

    def test_reload(self):

        # First load no need to redo feeds
        self.assertTrue(self.db_test.reload())

        # Loaded no need to redo feeds
        self.assertFalse(self.db_test.reload())
        self.assertEqual(self.db_test.feeds['Feed-1'].url, "http://google.com")
        self.assertEqual(self.db_test.feeds['Feed-1'].id, 1)
        self.assertEqual(self.db_test.feeds['Feed-1'].name, 'Test_Google')
        self.assertEqual(self.db_test.feeds['Feed-1'].frequency, 300)
        self.assertIsInstance(self.db_test.feeds['Feed-1'], Feed)

        # Test Subscriptions

        self.assertEqual(self.db_test.subscriptions['Subscription-1'].name, 'Test-Subscription')
        self.assertIsInstance(self.db_test.subscriptions['Subscription-1'], Subscription)

    @classmethod
    def setUpClass(cls):
        if path.exists(db_test_file):
            rm(db_test_file)
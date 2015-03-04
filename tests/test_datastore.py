__author__ = 'Dirrk'
import unittest

from os import remove as rm
from os import path
from app.rss.Feed import Feed
from app.rss.Subscription import Subscription

db_file = "C:\\Users\\derek_000\\PycharmProjects\\TorrentDownloader\\data\\test2_database.db"
db_test_file = "C:\\Users\\derek_000\\PycharmProjects\\TorrentDownloader\\data\\test_database.db"
from lib.DataStore import DataStore

KEEP_TEST_FILE = False


class TestDataStoreObject(unittest.TestCase):
    def setUp(self):
        self.longMessage = True
        self.db = DataStore(db_file)
        self.assertEqual(self.db.modified, 0)

        self.db_test = DataStore(db_test_file)
        self.db_test.create()
        self.db_test.add_feed(Feed(0, "http://google.com", "Test_Google", 300))
        a = Subscription(0, "Test-Subscription", 1)
        a.add_episode("S01E01")
        self.db_test.add_subscription(a)

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

        conn.close()

    def test_reload(self):

        # First load need to redo feeds
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
        self.assertGreater(len(self.db_test.subscriptions['Subscription-1'].episodes), 0)

    def test_update_subscription(self):

        self.db_test.reload()

        sub = self.db_test.subscriptions['Subscription-1']
        self.db_test.subscriptions['Subscription-2'] = Subscription(2, "Subscription2", 1, {})
        sub.add_episode('S01E02')
        self.assertEqual(len(sub.episodes), 2)

        # Add Subscription
        self.assertEqual(self.db_test.subscriptions['Subscription-2'].id, 2)
        self.assertEqual(self.db_test.subscriptions['Subscription-2'].feedId, 1)

        # Save sub into db
        self.db_test.update_subscription(sub)

        # Reload from scratch
        self.db_test.reload()

        sub1 = self.db_test.subscriptions['Subscription-1']
        self.assertEqual(len(sub1.episodes), 2)

        print "Keys:", self.db_test.subscriptions
        self.assertEqual(len(self.db_test.subscriptions.keys()), 4)

    def update_feed(self):

        self.assertTrue(self.db_test.reload())

        feed = self.db_test.feeds['Feed-1']
        self.assertEqual(feed.id, 1)
        self.assertEqual(feed.last_pub, 0)

        # Declare arbitrary number for new last_pub
        new_pub = 100000
        feed.last_pub = new_pub

        # Changed local variable
        self.assertEqual(feed.last_pub, new_pub)

        # Which was a pointer to that feed
        self.assertEqual(self.db_test.feeds['Feed-1'].last_pub, new_pub)

        # Force loaded without saving should be back to 0
        self.db_test.load()
        self.assertEqual(self.db_test.feeds['Feed-1'].last_pub, 0)

        # Manually change again then save it then load and prove
        self.db_test.feeds['Feed-1'].last_pub = new_pub
        self.db_test.update_feed(self.db_test.feeds['Feed-1'])
        self.db_test.load()
        self.assertEqual(self.db_test.feeds['Feed-1'].last_pub, new_pub)

    @classmethod
    def setUpClass(cls):
        if path.exists(db_test_file):
            rm(db_test_file)
        if path.exists(db_file):
            rm(db_file)

    @classmethod
    def tearDownClass(cls):
        if KEEP_TEST_FILE is not True:
            rm(db_test_file)
            rm(db_file)
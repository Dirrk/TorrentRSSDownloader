__author__ = 'Dirrk'
import unittest
import shutil

from os import remove as rm
from os import path
from app.rss.Feed import Feed
from app.rss.Subscription import Subscription


db_folder = "C:\\Users\\derek_000\\PycharmProjects\\TorrentDownloader\\data\\"
db_file = db_folder + "test2_database.db"
db_test_file = db_folder + "test_database.db"
db_test_upgrade_files = [
    {"original_file": "torrents-version-1.db", "file": "test-torrents-version-1.db", "Version": 1},
    {"original_file": "torrents-version-2.db", "file": "test-torrents-version-2.db", "Version": 2},
    {"original_file": "torrents-version-3.db", "file": "test-torrents-version-3.db", "Version": 3},
    {"original_file": "torrents-version-4.db", "file": "test-torrents-version-4.db", "Version": 4},
    {"original_file": "torrents-version-5.db", "file": "test-torrents-version-5.db", "Version": 5}
]

import lib.DataStore as db

KEEP_TEST_FILE = False


class TestDataStoreObject(unittest.TestCase):
    def setUp(self):
        self.longMessage = True
        self.db = db.DataStore(db_file)
        self.assertEqual(self.db.modified, 0)

        self.db_test = db.DataStore(db_test_file)
        self.db_test.create()
        self.assertEqual(self.db_test.db_version, db.__DB_VERSION__)
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

        for a in conn.execute("SELECT * FROM SETTINGS WHERE id='Feeds'").fetchall():
            self.assertGreater(int(a[1]), 0)
            print "Found: ", a

        conn.close()

    def test_reload(self):

        # First load need to redo feeds
        if KEEP_TEST_FILE is False:
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
            try:
                rm(db_test_file)
                rm(db_file)
            except:
                pass


class TestDataStoreVersion(unittest.TestCase):
    def setUp(self):
        self.longMessage = True
        for a_db_file in db_test_upgrade_files:
            if path.exists(db_folder + a_db_file['file']) is True:
                rm(db_folder + a_db_file['file'])
        for a_db_file in db_test_upgrade_files:
            shutil.copyfile(db_folder + a_db_file['original_file'], db_folder + a_db_file['file'])

    def tearDown(self):
        for a_db_file in db_test_upgrade_files:
            if path.exists(db_folder + a_db_file['file']) is True and KEEP_TEST_FILE is False:
                rm(db_folder + a_db_file['file'])

    def test_verify_sql_change(self):
        import sqlite3

        conn = sqlite3.connect(db_folder + db_test_upgrade_files[0]['file'])
        c = conn.cursor()

        verifier = db.verify_sql_change(c, "SELECT version FROM Settings WHERE name='Feeds'", 1, 'Settings', True)
        print verifier
        self.assertTrue(verifier['ret'], "Settings[Feeds] == 1 but it didn't because: " + verifier['info'])
        self.assertEqual(verifier['info'], 'Success')

        verifier = db.verify_sql_change(c, "SELECT nocolumn FROM Settings WHERE name='Feeds'", 1, 'Settings', True)
        print verifier
        self.assertFalse(verifier['ret'], "How did this column exist?:" + verifier['info'])
        self.assertRegexpMatches(verifier['info'], 'Failed.because.of.syntax.*')

        verifier = db.verify_sql_change(c, "SELECT version FROM Settings WHERE name='Feeds'", 2, 'Settings', True)
        print verifier
        self.assertFalse(verifier['ret'], "Feeds in settings should equal 1 not 2")
        self.assertRegexpMatches(verifier['info'], 'Failed.because.value.*')

        verifier = db.verify_sql_change(c, "SELECT version FROM SettingsBak WHERE name='Feeds'", 2, 'SettingsBak',
                                        True)
        print verifier
        self.assertFalse(verifier['ret'], "SettingsBak should not exist!")
        self.assertRegexpMatches(verifier['info'], 'Failed.to.create.database.table.*')
        conn.close()

    def test_get_db_version(self):
        import sqlite3

        for tests in db_test_upgrade_files:
            conn = sqlite3.connect(db_folder + tests['file'])
            ver = db.get_db_version(conn)
            self.assertEqual(ver, tests['Version'])
            conn.close()

    def test_upgrade_to_2(self):

        for tests in [test for test in db_test_upgrade_files if test['Version'] <= 2]:
            db_store = db.DataStore(db_folder + tests['file'])
            self.assertTrue(db_store.upgrade(2))
            self.assertEqual(db_store.db_version, 2)

    def test_upgrade_to_3(self):
        for tests in [test for test in db_test_upgrade_files if test['Version'] <= 3]:
            db_store = db.DataStore(db_folder + tests['file'])
            self.assertTrue(db_store.upgrade(3))
            self.assertEqual(db_store.db_version, 3)

    def test_upgrade_to_4(self):
        for tests in [test for test in db_test_upgrade_files if test['Version'] <= 4]:
            db_store = db.DataStore(db_folder + tests['file'])
            self.assertTrue(db_store.upgrade(4))
            self.assertEqual(db_store.db_version, 4)

    def test_create_upgrade(self):
        for tests in db_test_upgrade_files:
            db_store = db.DataStore(db_folder + tests['file'])
            self.assertTrue(db_store.create())
            self.assertEqual(db_store.db_version, db.__DB_VERSION__)

    def test_upgrade_to_fake_version(self):
        db_store = db.DataStore(db_folder + db_test_upgrade_files[0]['file'])
        self.assertFalse(db_store.upgrade(db.__DB_VERSION__ + 1))

    def test_get_settings(self):
        import sqlite3

        conn = sqlite3.connect(db_folder + db_test_upgrade_files[2]['file'])
        self.assertGreaterEqual(db.get_settings_value(conn, "Feeds", int), 1)
        self.assertIsNone(db.get_settings_value(conn, "SomeValueNotinSettings"))
        conn.close()
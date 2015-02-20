__author__ = 'Dirrk'

import unittest

from lib.DataStore import DataStore
import os
import app.plex.plex as plex
from app.rss.Subscription import Subscription
from app.rss.Feed import Feed
from app.rss.Item import Item
from app.torrent.Torrent import Torrent
import app.settings as settings

DB_FILE = "C:\\Users\\derek_000\\PycharmProjects\\TorrentDownloader\\data\\integration_test_database.db"
KEEP_FILE = True


class TestIntegrationOfApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)

    def setUp(self):
        self.db = DataStore(DB_FILE)
        self.db.create()

    # @unittest.skip("Not ready")
    def test_everything(self):

        self.db.load()
        feed_id = self.db.add_feed(Feed(0, settings.FEED[0], "HDTV"))

        # Test for proof
        self.assertEqual(feed_id, 1)

        api = plex.ApiHelper()
        shows = api.get_all_shows(settings.PLEX_TV_SECTION)
        for show in shows:
            a_show = Subscription(0, show.title, feed_id)
            eps = plex.PlexHelper.get_se_array(show)
            for ep in eps:
                a_show.add_episode(ep)
            a_show.set_option("reg_allow", plex.PlexHelper.generate_regex(show))
            a_show.set_option("episode_match", True)
            a_show.enabled = 1
            a_show.plex_id = show.id

            # Add to DB
            self.assertGreater(self.db.add_subscription(a_show), 0)

        my_feed = self.db.feeds['Feed-' + str(feed_id)]

        self.assertIsInstance(my_feed, Feed)

        items = my_feed.fetch_items()
        for key in self.db.subscriptions:
            sub = self.db.subscriptions[key]
            matched = sub.match(items)
            if matched is not None and len(matched) > 0:
                for match in matched:
                    print "Found matches:", match.title
                    self.assertIsInstance(match, Item)
                    a_torrent = Torrent(match.link)
                    a_torrent.subscriptionId = sub.id
                    a_torrent.final_location = plex.PlexHelper.find_location(sub.plex_id, match.episode)
                    if a_torrent.download() is True:
                        self.db.add_torrent(a_torrent)
                    else:
                        print "Torrent failed to download"

                self.db.update_subscription(sub)

        # TODO Bug will download a tv pack that matches which is not the intended case

        self.db.update_feed(my_feed)
        self.assertEqual(True, True)

    def test_nothing(self):
        self.assertEqual(True, True)

    @classmethod
    def tearDownClass(cls):
        if KEEP_FILE is False and os.path.exists(DB_FILE):
            os.remove(DB_FILE)
__author__ = 'Dirrk'

import unittest
from datetime import datetime as date
import time

from app.rss.Feed import Feed
from app.rss.Item import Item
from app.rss.Subscription import Subscription
import requests


""""
 Testing features / objects in this application
"""


class TestRSSSite(unittest.TestCase):
    def test_rssSite(self):
        r = requests.get(
            "https://www.iptorrents.com/torrents/rss?download;l66;l65;l5;l4;u=1216603;tp=TOKEN")
        self.assertRegexpMatches(r.content, 'rss', "iptorrents is not responding correctly")


class TestItemObject(unittest.TestCase):
    def setUp(self):
        self.ia = Item(
            '<item><title>The Late Late Show 2014 01 30 Martellus Bennett 720p HDTV x264-CROOKS</title><link>https://iptorrents.com/download.php/1310285/The.Late.Late.Show.2014.01.30.Martellus.Bennett.720p.HDTV.x264-CROOKS.torrent?torrent_pass=TOKEN</link><pubDate>Sat, 31 Jan 2015 19:19:28 +0000</pubDate><description>1.12 GB; TV/x264</description></item>')
        self.ib = Item(
            '<item><title>Mountain Men S01E05 720p WEBRip H264-TURBO</title><link>https://iptorrents.com/download.php/1310224/Mountain.Men.S01E05.720p.WEBRip.H264-TURBO.torrent?torrent_pass=TOKEN</link><pubDate>Sat, 31 Jan 2015 17:50:06 +0000</pubDate><description>855 MB; TV/x264</description></item>')

    def test_item(self):
        self.assertIsInstance(self.ia, Item)
        self.assertIsInstance(self.ib, Item)

    def test_seasonAndEpisodes(self):
        self.assertEqual(self.ia.episode, "20140130")
        self.assertEqual(self.ib.episode, "S01E05")

    def test_Size(self):
        self.assertGreaterEqual(self.ia.size, 1000)
        self.assertGreaterEqual(self.ib.size, 850)

    def test_Title(self):
        self.assertRegexpMatches(self.ia.title, 'The.Late.Late.Show.*')
        self.assertRegexpMatches(self.ib.title, 'Mountain.Men*')

    def test_Quality(self):
        self.assertGreaterEqual(self.ia.quality, 720)
        self.assertGreaterEqual(self.ib.quality, 720)

    def test_Times(self):
        iatimestring = date.strftime(self.ia.pubDate, "%a, %d %b %Y %H:%M:%S +0000")
        ibtimestring = date.strftime(self.ib.pubDate, "%a, %d %b %Y %H:%M:%S +0000")

        self.assertEqual(date.strptime(iatimestring, "%a, %d %b %Y %H:%M:%S +0000").hour, 19)
        self.assertEqual(date.strptime(iatimestring, "%a, %d %b %Y %H:%M:%S +0000").minute, 19)
        self.assertEqual(date.strptime(ibtimestring, "%a, %d %b %Y %H:%M:%S +0000").hour, 17)
        self.assertEqual(date.strptime(ibtimestring, "%a, %d %b %Y %H:%M:%S +0000").minute, 50)

    def test_badData(self):
        with self.assertRaises(TypeError):
            Item("TestBlahBlah")


class TestFeedObject(unittest.TestCase):
    def setUp(self):
        self.myFeed = Feed(1,
                           'https://www.iptorrents.com/torrents/rss?download;l66;l65;l5;l4;u=1216603;tp=TOKEN',
                           "My Name", 3)

    def test_basic_values(self):
        self.assertEqual(self.myFeed.frequency, 3)
        self.assertEqual(self.myFeed.name, "My Name")
        self.assertEqual(self.myFeed.id, 1)

    def test_fetch(self):
        values = self.myFeed.fetch_items()
        self.assertGreaterEqual(len(values), 1)
        self.assertIsInstance(values[0], Item)
        self.myFeed.last_pub = values[0].pubDate
        self.assertEqual(self.myFeed.last_pub, values[0].pubDate)

    def test_update_cycle(self):
        self.myFeed.fetch_items()
        self.assertFalse(self.myFeed.update_cycle())
        time.sleep(5)
        self.assertTrue(self.myFeed.update_cycle())


class TestSubscriptionObject(unittest.TestCase):
    def setUp(self):
        self.items = []
        self.items.append(Item(
            '<item><title>The Late Late Show 2014 01 30 Martellus Bennett 720p HDTV x264-CROOKS</title><link>https://iptorrents.com/download.php/1310285/The.Late.Late.Show.2014.01.30.Martellus.Bennett.720p.HDTV.x264-CROOKS.torrent?torrent_pass=TOKEN</link><pubDate>Sat, 31 Jan 2015 19:19:28 +0000</pubDate><description>1.12 GB; TV/x264</description></item>'))
        self.items.append(Item(
            '<item><title>Mountain Men S01E05 720p WEBRip H264-TURBO</title><link>https://iptorrents.com/download.php/1310224/Mountain.Men.S01E05.720p.WEBRip.H264-TURBO.torrent?torrent_pass=TOKEN</link><pubDate>Sat, 31 Jan 2015 17:50:06 +0000</pubDate><description>855 MB; TV/x264</description></item>'))
        self.sub = Subscription(1, "Test Mountain Men", 12345, {})
        self.assertEqual(self.sub.id, 1)
        self.assertEqual(self.sub.name, "Test Mountain Men")
        self.assertEqual(self.sub.feedId, 12345)


    def test_episodes(self):
        self.assertEqual(self.sub.add_episode("S01E01"), 1)
        self.assertEqual(self.sub.add_episode("S01E02"), 2)
        self.assertEqual(self.sub.add_episode("S01E02"), 2)

    def test_options(self):
        """
        options['reg_allow'] = inopts.reg_allow if inopts.get('reg_allow') is not None else ""
        options['reg_exclude'] = inopts.reg_exclude if inopts.get('reg_exclude') is not None else "555DO-NOT-MATCH-THIS-REGEX-ESCAPE555"
        options['enabled'] = inopts.enabled if inopts.get('enabled') is not None else False
        options['waitTime'] = inopts.waitTime if inopts.get('waitTime') is not None else 0  # Hours
        options['lastMatched'] = inopts.lastMatched if inopts.get('lastMatched') is not None else datetime.datetime.utcfromtimestamp(0)
        options['minSize'] = inopts.minSize if inopts.get('minSize') is not None else 0
        options['maxSize'] = inopts.maxSize if inopts.get('maxSize') is not None else 1000000000  # Max of one petabyte ;)
        options['quality'] = inopts.quality if inopts.get('quality') is not None else -1
        options['episode_match'] = inopts.episode_match if inopts.get('episode_match') is not None else False
        options['onlyOnce'] = inopts.onlyOnce if inopts.get('onlyOnce') is not None else False
        """
        self.assertEqual(self.sub.__options__.get('reg_exclude'), "555DO-NOT-MATCH-THIS-REGEX-ESCAPE555")
        self.assertFalse(self.sub.__options__.get('enabled'))
        self.assertFalse(self.sub.__options__.get('episode_match'))
        self.assertFalse(self.sub.__options__.get('onlyOnce'))
        self.assertEqual(self.sub.__options__.get('waitTime'), 0)
        self.assertEqual(self.sub.__options__.get('minSize'), 0)
        self.assertEqual(self.sub.__options__.get('maxSize'), 1000000000)
        self.assertEqual(self.sub.__options__.get('quality'), -1)
        self.assertLess(self.sub.__options__.get('lastMatched'), time.time())

        import json

        print json.dumps(self.sub.__options__)


    def test_match(self):
        """
        Todo
        :return:
        """
        self.sub.set_option("enabled", True)
        self.assertTrue(self.sub.__options__.get('enabled'))
        self.sub.set_option("episode_match", True)
        self.sub.set_option("reg_allow", "Mountain.Men*")
        matches = self.sub.match(self.items)
        print "Matches object:", matches
        self.assertEqual(len(matches), 1)
        self.assertIsInstance(matches[0], Item)
        self.assertEqual(matches[0].episode, "S01E05")
        self.assertEqual(len(self.sub.episodes), 1)
        self.assertEqual(self.sub.add_episode("S01E01"), 2)
        self.assertEqual(self.sub.add_episode("S01E02"), 3)
        matches2 = self.sub.match(self.items)
        self.assertEqual(len(matches2), 0)
        self.assertEqual(len(self.sub.episodes), 3)
        print "Matches object:", matches2
        for eps in self.sub.episodes:
            print "Episodes:", eps


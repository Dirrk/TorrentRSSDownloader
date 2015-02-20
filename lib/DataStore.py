__author__ = 'Dirrk'

import sqlite3
import logging
import json

import app.settings as settings
from app.rss.Feed import Feed
from app.rss.Subscription import Subscription
from app.torrent.Torrent import Torrent
import os.path as path


class DataStore():
    def __init__(self, a_file=None):
        self.feeds = {}
        self.subscriptions = {}
        self.torrents = {}
        if a_file is None:
            a_file = settings.DATA_FILE
        self.__db_file__ = a_file
        self.modified = 0

    def create(self):

        if not path.isfile(self.__db_file__):
            logging.info("Creating db")
            conn = sqlite3.connect(self.__db_file__)
            c = conn.cursor()

            c.execute(
                '''
                CREATE TABLE Feeds
                (
                  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  url TEXT NOT NULL,
                  frequency INTEGER NOT NULL DEFAULT '300',
                  last_pub INTEGER NOT NULL DEFAULT '0'
                );
                '''
            )
            c.execute(
                '''
                CREATE TABLE Settings
                (
                    name TEXT NOT NULL,
                    version INTEGER NOT NULL DEFAULT '0'
                );
                '''
            )
            c.execute(
                '''
                CREATE TABLE SubscriptionEpisodes
                (
                    subscriptionid INTEGER NOT NULL,
                    episode TEXT NOT NULL
                );
                '''
            )
            c.execute(
                '''
                CREATE TABLE Subscriptions
                (
                    id	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    feedid INTEGER NOT NULL,
                    options TEXT NOT NULL DEFAULT '{"reg_allow":"","onlyOnce":false,"episode_match":true,"waitTime":0,"preferred_release":"","maxSize":1000000000,"lastMatched":0,"minSize":0,"reg_exclude":"555DO-NOT-MATCH-THIS-REGEX-ESCAPE555","quality":-1}',
                    enabled INTEGER DEFAULT '0',
                    plex_id INTEGER DEFAULT '0'
                );
                '''
            )
            c.execute(
                '''
                CREATE TABLE `Torrents` (
                    link TEXT NOT NULL,
                    status INTEGER NOT NULL DEFAULT '0',
                    subscriptionid	INTEGER NOT NULL,
                    folder TEXT NOT NULL PRIMARY KEY,
                    file TEXT,
                    final_location TEXT
                );
                '''
            )
            c.execute("INSERT INTO SETTINGS VALUES ('Feeds', 1);")
            conn.commit()
            self.modified = 1
            conn.close()

        else:
            logging.info("Upgrade db")

    def load(self):
        """
        Create create database if file doesn't exist
        Load Feeds
        Load Subscriptions
        TODO: Load torrents
        :return: Boolean if (feeds needed to be recreated)
        """
        if not path.isfile(self.__db_file__):
            logging.warn("File does not exist %s" % self.__db_file__)
            self.create()
        else:
            self.modified = -1
            self.reload()

        return True

    def reload(self):
        """

        :return:
        """
        if not path.isfile(self.__db_file__):
            logging.warn("File does not exist cannot reload %s" % self.__db_file__)
            self.create()
            return True

        else:
            # Connect to sql
            conn = sqlite3.connect(self.__db_file__)

            reload_feeds = self.modified < get_modified(conn)

            if reload_feeds:
                self.feeds = get_feeds(conn)

            # Retrieve data
            self.subscriptions = get_subscriptions(conn)
            self.torrents = get_torrents(conn)
            self.modified = get_modified(conn)

            conn.close()
            return reload_feeds

    # Called after a subscription has been matched which is the only time anything could change
    def update_subscription(self, sub):

        if not path.isfile(self.__db_file__):
            self.create()

        conn = sqlite3.connect(self.__db_file__)

        new_opts = json.dumps(sub.__options__)

        c = conn.cursor()

        c.execute(
            '''
              UPDATE Subscriptions SET feedid=?, enabled=?, plex_id=?, options=? WHERE id=?
            ''', (sub.feedId, sub.enabled, sub.plex_id, new_opts, sub.id)
        )
        c.execute(
            '''
              DELETE FROM SubscriptionEpisodes WHERE subscriptionid=?
            ''', (sub.id,)
        )
        for episode in sub.episodes:
            c.execute(
                '''
                  INSERT INTO SubscriptionEpisodes(episode, subscriptionid) VALUES (?, ?)
                ''', (episode, sub.id)
            )
        conn.commit()
        conn.close()

    # Called every time feed runs
    def update_feed(self, feed):

        if not path.isfile(self.__db_file__):
            self.create()

        conn = sqlite3.connect(self.__db_file__)

        c = conn.cursor()

        c.execute(
            '''
              UPDATE Feeds SET last_pub=? WHERE id=?
            ''', (feed.last_pub, feed.id)
        )
        conn.commit()
        conn.close()

    # Add Feed
    def add_feed(self, feed):
        conn = sqlite3.connect(self.__db_file__)
        c = conn.cursor()

        c.execute(
            '''
              INSERT INTO Feeds(url, name, frequency, last_pub) VALUES (?, ?, ?, ?);
            ''', (feed.url, feed.name, feed.frequency, feed.last_pub)
        )
        ret_id = c.lastrowid
        conn.commit()
        conn.close()
        feed.id = ret_id
        self.feeds['Feed-' + str(ret_id)] = feed
        return ret_id

    def add_subscription(self, sub):
        conn = sqlite3.connect(self.__db_file__)
        c = conn.cursor()
        c.execute(
            '''
              INSERT INTO Subscriptions(name, feedid) VALUES (?, ?);
            ''', (sub.name, sub.feedId)
        )
        sub.id = c.lastrowid
        conn.commit()
        conn.close()
        self.update_subscription(sub)
        self.subscriptions['Subscription-' + str(sub.id)] = sub
        return sub.id

    def add_torrent(self, tor):
        conn = sqlite3.connect(self.__db_file__)
        c = conn.cursor()
        c.execute(
            '''
              INSERT INTO Torrents(link,status,subscriptionid,file,folder,final_location) VALUES (?,?,?,?,?,?)
            ''', (tor.link, tor.status, tor.subscriptionId, tor.file, tor.folder, tor.final_location)
        )
        conn.commit()
        conn.close()
        self.torrents[tor.folder] = tor
        return tor.folder

    def update_torrent(self, tor):
        conn = sqlite3.connect(self.__db_file__)
        c = conn.cursor()
        c.execute(
            '''
              UPDATE Torrents SET link=?, status=?, subscriptionid=?,file=?, final_location=? WHERE folder=?
            ''', (tor.link, tor.status, tor.subscriptionId, tor.file, tor.final_location, tor.folder)
        )
        conn.commit()
        conn.close()
        return tor.folder


def get_modified(conn):

    c = conn.cursor()

    c.execute('SELECT version FROM SETTINGS WHERE name="Feeds"')

    db_mod = c.fetchone()
    if db_mod is None:
        return 0
    else:
        return int(db_mod[0])


def get_feeds(conn):
    feeds = {}

    c = conn.cursor()

    c.execute(
        '''
            SELECT id, url, name, frequency, last_pub FROM Feeds;
        '''
    )
    for feed in c.fetchall():
        # id, url, name="new feed", frequency=300
        new_feed = Feed(int(feed[0]), feed[1], feed[2], int(feed[3]))
        try:
            new_feed.last_run = float(feed[4])
        except Exception:
            pass

        feeds['Feed-' + str(feed[0])] = new_feed
        logging.info('Added Feed-' + str(feed[0]))

    return feeds


def get_subscriptions(conn):

    subscriptions = {}

    c = conn.cursor()

    c.execute(
        '''
            SELECT id, name, feedid, plex_id, options FROM Subscriptions WHERE enabled = 1;
        '''
    )
    for sub in c.fetchall():

        opts = {}
        try:
            opts = json.loads(sub[4])
            for key in opts.keys():
                print key
        except Exception as e:
            print "Exception"
            print e.message
            opts = {}

        new_sub = Subscription(int(sub[0]), sub[1], int(sub[2]), opts)

        new_sub.plex_id = int(sub[3])

        subscriptions['Subscription-' + str(sub[0])] = new_sub
        logging.info("Added Subscription-" + str(sub[0]))
        episodes = get_episodes(conn, new_sub.id)

        for episode in episodes:
            new_sub.add_episode(episode)

    return subscriptions


def get_episodes(conn, id):
    d = conn.cursor()
    d.execute(
        '''
          SELECT episode FROM SubscriptionEpisodes WHERE subscriptionid=?
        ''', (id,)
    )
    episodes = []
    for ep in d.fetchall():
        episodes.append(ep[0])

    return episodes

def get_torrents(conn):
    d = conn.cursor()
    d.execute(
        '''
            SELECT link, status, subscriptionid, folder, file, final_location FROM Torrents WHERE status < 4
        '''
    )
    torrents = {}
    for tor in d.fetchall():
        a_torrent = Torrent(tor[0], int(tor[1]), tor[4], tor[3], tor[2])
        a_torrent.final_location = tor[5]
        torrents[a_torrent.folder] = a_torrent

    return torrents
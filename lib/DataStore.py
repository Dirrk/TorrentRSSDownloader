__author__ = 'Dirrk'

import sqlite3
import logging
import json

import app.settings as settings
from app.rss.Feed import Feed
from app.rss.Subscription import Subscription
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
                    options TEXT NOT NULL DEFAULT '{"reg_allow":"","onlyOnce":false,"episode_match":false,"enabled":false,"waitTime":0,"preferred_release":"","maxSize":1000000000,"lastMatched":0,"minSize":0,"reg_exclude":"555DO-NOT-MATCH-THIS-REGEX-ESCAPE555","quality":-1}'
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
    def update_subscription(self, sub, episode=None):

        if not path.isfile(self.__db_file__):
            self.create()

        conn = sqlite3.connect(self.__db_file__)

        new_opts = json.dumps(sub.__options__)

        c = conn.cursor()
        if episode is not None:
            c.execute(
                '''
                  INSERT INTO SubscriptionEpisodes(episode, subscriptionid) VALUES (?, ?)
                ''', (episode, sub.id)
            )
        c.execute(
            '''
              UPDATE Subscriptions SET options=? WHERE id=?
            ''', (new_opts, sub.id)
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
            SELECT id, name, feedid, options FROM Subscriptions;
        '''
    )
    for sub in c.fetchall():

        opts = {}
        try:
            opts = json.loads(sub[3])
            for key in opts.keys():
                print key
        except Exception as e:
            print "Exception"
            print e.message
            opts = {}

        new_sub = Subscription(int(sub[0]), sub[1], int(sub[2]), opts)
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
    # TODO Complete torrent setup
    return {}
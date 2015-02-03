__author__ = 'Dirrk'

import sqlite3
import logging

import os.path as path


class DataStore():
    def __init__(self, a_file):
        self.feeds = {}
        self.subscriptions = {}
        self.torrents = {}
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
                  last_pub TEXT NOT NULL
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
            # self.upgrade()

    def load(self):
        """
        Create create database if file doesn't exist
        Load Feeds
        Load Subscriptions
        TODO: Load torrents
        :return: None
        """
        if not path.isfile(self.__db_file__):
            logging.warn("File does not exist %s" % self.__db_file__)
            # self.create()

        else:

            conn = sqlite3.connect(self.__db_file__)

            # Load modified version
            self.modified = get_modified(conn)
            self.feeds = get_feeds(conn)
            self.subscriptions = get_subscriptions(conn)
            self.torrents = get_torrents(conn)

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
    return feeds


def get_subscriptions(conn):
    subscriptions = {}
    return subscriptions


def get_torrents(conn):
    # TODO Complete torrent setup
    return {}
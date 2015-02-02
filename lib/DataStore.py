__author__ = 'Dirrk'

import sqlite3
import logging

import os.path as path


# from app.rss.Subscription import Subscription


class DataStore():
    def __init__(self, a_file):
        self.feeds = {}
        self.subscriptions = {}
        self.torrents = {}
        self.__db_file__ = a_file
        self.modified = 0

    def load(self):
        """
        Create create database if file doesn't exist
        Load Feeds
        Load Subscriptions
        TODO: Load torrents
        :return: None
        """
        if not path.isfile(self.__db_file__):
            pass
            logging.warn("File does not exist %s" % self.__db_file__)
            # self.create()

        else:

            conn = sqlite3.connect(self.__db_file__)

            if get_modified(conn) == self.modified:
                # self.feeds = load_feeds(self.__db_file__)
                logging.info("Not modified")
            else:
                self.modified = get_modified(conn)
                logging.info("Modified")
                # load_sub_episodes(self.__db_file__, self.subscriptions)

                # TODO Complete torrent info
                # self.torrents = load_torrents(self.__db_file__)
            conn.close()


def get_modified(conn):

    c = conn.cursor()

    c.execute('SELECT version FROM SETTINGS WHERE name="Feeds"')

    db_mod = c.fetchone()
    if db_mod is None:
        return 0
    else:
        return int(db_mod[0])


def load_feeds(a_file):
    return a_file
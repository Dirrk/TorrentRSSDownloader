__author__ = 'Dirrk'

import sqlite3

import os.path as path

# from app.rss.Subscription import Subscription


class DataStore():
    def __init__(self, a_file):
        self.feeds = {}
        self.subscriptions = {}
        self.torrents = {}
        self.__db_file__ = a_file
        self.modifier = {
            "Feeds": 1,
            "Subscriptions": 1
        }

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
            # self.create()

        else:

            modifiers = get_modifiers(self.__db_file__)

            if modifiers["Feeds"] != self.modifier["Feeds"]:
                # self.feeds = load_feeds(self.__db_file__)
                self.modifier = modifiers["Feeds"]

            if modifiers["Subscriptions"] != self.modifier["Subscriptions"]:
                # self.subscriptions = load_subscriptions(self.__db_file__)
                self.modifier = modifiers["Subscriptions"]

                # load_sub_episodes(self.__db_file__, self.subscriptions)

                # TODO Complete torrent info
                # self.torrents = load_torrents(self.__db_file__)


def get_modifiers(file):
    conn = sqlite3.connect(file)
    c = conn.cursor()

    c.execute("SELECT table_name, version FROM Modifier")

    count = 0
    for row in c.fetchall():
        count += 1
        print row

    conn.close()

    return count


def load_feeds(file):
    pass
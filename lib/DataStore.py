__author__ = 'Dirrk'

import sqlite3
import logging
import json

import app.settings as settings
from app.rss.Feed import Feed
from app.rss.Subscription import Subscription
from app.torrent.Torrent import Torrent
import os.path as path


__DB_VERSION__ = 3


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
                    id TEXT NOT NULL PRIMARY KEY,
                    val TEXT NOT NULL DEFAULT '0'
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
                    final_location TEXT,
                    status_time INTEGER DEFAULT '0'
                );
                '''
            )
            c.execute("INSERT INTO SETTINGS VALUES ('DB_VERSION', ?);", str(__DB_VERSION__))
            c.execute("INSERT INTO SETTINGS VALUES ('Feeds', '1');")
            conn.commit()
            self.modified = 1
            conn.close()

        else:
            self.upgrade(__DB_VERSION__)

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
            if self.upgrade(__DB_VERSION__) is False:
                raise sqlite3.IntegrityError("Database failed to upgrade to current version!")

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

            reload_feeds = self.modified < get_settings_value(conn, "Feeds", int)

            if reload_feeds:
                self.feeds = get_feeds(conn)

            # Retrieve data
            self.subscriptions = get_subscriptions(conn)
            self.torrents = get_torrents(conn)
            self.modified = get_settings_value(conn, "Feeds", int)

            conn.close()
            return reload_feeds

    def upgrade(self, db_version=None):

        # Added for unit testing
        if db_version is None:
            db_version = __DB_VERSION__

        # Get the current db version
        current_version = get_db_version()
        count = -1

        while current_version != db_version and count <= db_version:

            conn = sqlite3.connect(self.__db_file__)
            c = conn.cursor()
            count += 1
            if current_version == 1:
                # run steps to upgrade
                c.execute(
                    '''
                      ALTER TABLE Torrents
                      ADD COLUMN status_time INTEGER DEFAULT '0'
                    ''')
                c.execute("INSERT INTO SETTINGS VALUES ('DB_VERSION', 2);")
                conn.commit()

            elif current_version == 2:
                # run steps to upgrade
                # Create Temporary Table
                c.execute(
                    '''
                        CREATE TABLE SettingsNew
                        (
                            id TEXT NOT NULL PRIMARY KEY,
                            val TEXT NOT NULL DEFAULT '0'
                        );
                    '''
                )
                # Fill with data
                c.execute("INSERT INTO SettingsNew SELECT * FROM Settings")

                # Change the version
                c.execute("UPDATE SettingsNew SET val = '3' WHERE id = 'DB_VERSION'")

                # Verify the version and creation
                if verify_sql_change(c, "SELECT val FROM SettingsNew WHERE id='DB_VERSION'", '3',
                                     'SettingsNew') is not True:
                    conn.rollback()
                    conn.close()
                    raise sqlite3.DatabaseError("Failed to upgrade to db_version 3")

                conn.commit()
                logging.info("Backed up changes and proceeding to complete upgrade")

                # Drop Settings Table
                c.execute("DROP TABLE Settings")

                # Rename Temporary Table to Settings
                c.execute("ALTER TABLE SettingsNew RENAME TO Settings")
                # verify
                if verify_sql_change(c, "SELECT val FROM Settings WHERE id='DB_VERSION'", '3',
                                     'Settings') is not True:
                    conn.rollback()
                    conn.close()
                    raise sqlite3.DatabaseError("Failed to finish table conversion for db_version 3")
                conn.commit()

            conn.close()
            current_version = get_db_version()

        if count > db_version:
            raise sqlite3.DatabaseError("Count broke upgrade loop!\r\nExpected Version: " + str(db_version) + '\r\n' +
                                        'Actual Version: ' + current_version)
        else:
            return True

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
              INSERT INTO Torrents(link,status,subscriptionid,file,folder,final_location,status_time) VALUES (?,?,?,?,?,
              ?,?)
            ''', (tor.link, tor.status, tor.subscriptionId, tor.file, tor.folder, tor.final_location, tor.status_time)
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
              UPDATE Torrents SET link=?, status=?, subscriptionid=?,file=?, final_location=?, status_time=?
              WHERE folder=?
            ''', (tor.link, tor.status, tor.subscriptionId, tor.file, tor.final_location, tor.status_time, tor.folder)
        )
        conn.commit()
        conn.close()
        return tor.folder

    def get_all_subscriptions(self):
        conn = sqlite3.connect(self.__db_file__)
        subscriptions = get_subscriptions(conn, True)
        conn.close()
        return subscriptions


def get_settings_value(conn, key, a_type=int):

    c = conn.cursor()

    c.execute('SELECT val FROM SETTINGS WHERE id=?', (str(key),))

    db_mod = c.fetchone()
    if db_mod is None:
        return None
    else:
        return a_type(db_mod[0])


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
            new_feed.last_pub = int(feed[4])
        except Exception as e:
            logging.exception(e)

        feeds['Feed-' + str(feed[0])] = new_feed
        logging.debug('Added Feed-' + str(feed[0]))

    return feeds


def get_subscriptions(conn, all_subs=False):

    subscriptions = {}

    c = conn.cursor()

    if all_subs is True:
        c.execute(
            '''
              SELECT id, name, feedid, plex_id, options FROM Subscriptions;
            '''
        )
    else:
        c.execute(
            '''
              SELECT id, name, feedid, plex_id, options FROM Subscriptions WHERE enabled = 1;
            '''
        )
    for sub in c.fetchall():

        opts = {}
        try:
            opts = json.loads(sub[4])

        except Exception as e:
            logging.exception(e)
            opts = {}

        new_sub = Subscription(int(sub[0]), sub[1], int(sub[2]), opts)

        new_sub.plex_id = int(sub[3])

        subscriptions['Subscription-' + str(sub[0])] = new_sub

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
            SELECT link, status, subscriptionid, folder, file, final_location, status_time FROM Torrents WHERE status < 4
        '''
    )
    torrents = {}
    for tor in d.fetchall():
        a_torrent = Torrent(tor[0], int(tor[1]), tor[4], tor[3], tor[2])
        a_torrent.final_location = tor[5]
        a_torrent.status_time = int(tor[6])
        torrents[a_torrent.folder] = a_torrent

    return torrents


def get_db_version(conn):
    d = conn.cursor()
    d.execute(
        '''
            PRAGMA table_info('Settings')
        '''
    )
    columns = d.fetchall()
    if len(columns) == 2:
        if columns[0][1] == 'name' and columns[1][1] == 'version':
            # 1 and 2
            d.execute("SELECT version FROM SETTINGS WHERE name='DB_VERSION'")
            db_mod = d.fetchone()
            if db_mod is None:
                return 1
            else:
                return 2

        elif columns[0][1] == 'id' and columns[1][1] == 'val':
            # 3 and up
            curr_version = get_settings_value(conn, 'DB_VERSION', int)
            if curr_version is not None:
                return curr_version
            else:
                raise sqlite3.DataError("Current version unknown")


# verify_sql_change(conn, c, "SELECT val FROM SettingsNew WHERE id='DB_VERSION'", '3', 'SettingsNew')
def verify_sql_change(cursor, get_one, should_equal, table_name):
    cursor.execute(get_one)

    the_value = cursor.fetchone()
    if the_value == should_equal:
        logging.info("Verified changes to table" + str(table_name))
        return True
    elif the_value is None:
        cursor.execute("PRAGMA table_info(?)", (str(table_name),))
        rows = cursor.fetchall()
        if rows is None:
            reason = "Failed to create database table" + str(table_name)
        else:
            reason = "Failed because of syntax in change for table", table_name, \
                     "\r\n\tColumnId\tName\tType\tdefault\tisPrimary\r\n"
            for row in rows:
                reason += "\t" + "\t".join(row) + "\r\n"
        logging.error(reason)
    else:
        logging.error("Failed because value: " + str(the_value) + " != " + str(should_equal))
    return False
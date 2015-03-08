__author__ = 'Dirrk'

import sqlite3
import logging
import json

import app.settings as settings
from app.rss.Feed import Feed
from app.rss.Subscription import Subscription
from app.torrent.Torrent import Torrent
import os.path as path


__DB_VERSION__ = 4


class DataStore():
    def __init__(self, a_file=None):
        self.feeds = {}
        self.subscriptions = {}
        self.torrents = {}
        if a_file is None:
            a_file = settings.DATA_FILE
        self.__db_file__ = a_file
        self.modified = 0
        self.db_version = None

    def create(self):

        if not path.isfile(self.__db_file__):
            logging.info("Creating db " + self.__db_file__)
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
                            plex_id INTEGER DEFAULT '0',
                            enabled INTEGER DEFAULT '1',
                            reg_allow TEXT DEFAULT '',
                            match_type TEXT DEFAULT 'episode',
                            preferred_release TEXT DEFAULT '',
                            max_size INTEGER DEFAULT '1000000000',
                            min_size INTEGER DEFAULT '0',
                            reg_exclude TEXT DEFAULT '555DO-NOT-MATCH-THIS-REGEX-ESCAPE555',
                            quality INTEGER DEFAULT '-1',
                            last_matched INTEGER DEFAULT '0'
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
            self.db_version = __DB_VERSION__
            conn.close()

        else:
            logging.info("Performing Upgrade on db file " + self.__db_file__)
            return self.upgrade(__DB_VERSION__)

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
            if self.db_version is None and self.upgrade(__DB_VERSION__) is False:
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
            conn.row_factory = dict_factory

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
        conn = sqlite3.connect(self.__db_file__)
        current_version = get_db_version(conn)
        conn.close()

        count = -1

        while current_version != db_version and count <= db_version:

            file = self.__db_file__
            conn = sqlite3.connect(self.__db_file__)

            c = conn.cursor()
            if current_version <= 1:
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
                c.execute("UPDATE SettingsNew SET val = 3 WHERE id = 'DB_VERSION'")

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

            elif current_version == 3:
                # run steps to upgrade to 4
                # Create Temporary Table
                c.execute(
                    '''
                        CREATE TABLE SubscriptionsBak
                        (
                            id	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            feedid INTEGER NOT NULL,
                            plex_id INTEGER DEFAULT '0',
                            enabled INTEGER DEFAULT '1',
                            reg_allow TEXT DEFAULT '',
                            match_type TEXT DEFAULT 'episode',
                            preferred_release TEXT DEFAULT '',
                            max_size INTEGER DEFAULT '1000000000',
                            min_size INTEGER DEFAULT '0',
                            reg_exclude TEXT DEFAULT '555DO-NOT-MATCH-THIS-REGEX-ESCAPE555',
                            quality INTEGER DEFAULT '-1',
                            last_matched INTEGER DEFAULT '0'
                        );
                    '''
                )
                # Fill with data
                c.execute('''
                      INSERT INTO SubscriptionsBak (id, name, feedid, plex_id, enabled) SELECT id, name, feedid,
                      plex_id, enabled FROM Subscriptions
                          ''')
                # Change the version
                c.execute("UPDATE Settings SET val = 4 WHERE id = 'DB_VERSION'")
                conn.commit()

                # Retrieve options
                c.execute("SELECT id, options FROM Subscriptions")
                all_subs = []
                for sub in c.fetchall():
                    if sub is not None and len(sub) == 2:
                        id = sub[0]
                        options = json.loads(sub[1])
                        if options.get('episode_match') is True:
                            match_type = 'episode'
                        else:
                            match_type = 'once'

                        a_sub_arr = [options.get('reg_allow'), match_type, options.get('preferred_release'),
                                     options.get('maxSize'), options.get('minSsize'), options.get('reg_exclude'),
                                     options.get('quality'), options.get('lastMatched'), id]

                        all_subs.append(a_sub_arr)

                # Update DB
                for a_sub in all_subs:
                    c.execute('''
                                UPDATE SubscriptionsBak SET
                                    reg_allow=?,
                                    match_type=?,
                                    preferred_release=?,
                                    max_size=?,
                                    min_size=?,
                                    reg_exclude=?,
                                    quality=?,
                                    last_matched=?
                                WHERE id=?
                              ''', a_sub)

                # Drop Settings Table
                c.execute("DROP TABLE Subscriptions")

                # Rename Temporary Table to Settings
                c.execute("ALTER TABLE SubscriptionsBak RENAME TO Subscriptions")

                conn.commit()

            else:
                count += 1

            current_version = get_db_version(conn)
            conn.close()

        self.db_version = current_version

        if count > db_version or current_version != db_version:
            logging.warn("Count was greater than db_version")
            return False
        else:
            return True

    # Called after a subscription has been matched which is the only time anything could change
    def update_subscription(self, sub):

        if not path.isfile(self.__db_file__):
            self.create()

        conn = sqlite3.connect(self.__db_file__)

        c = conn.cursor()

        c.execute(
            '''
              UPDATE Subscriptions SET name=?, feedid=?, plex_id=?, enabled=?, reg_allow=?, match_type=?,
              preferred_release=?, max_size=?, min_size=?, reg_exclude=?, quality=?, last_matched=? WHERE id=?
            ''', (sub.name, sub.feedId, sub.plex_id, sub.enabled, sub.reg_allow, sub.match_type, sub.preferred_release,
                  sub.max_size, sub.min_size, sub.reg_exclude, sub.quality, sub.last_matched, sub.id)
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
            ''', (feed.last_run, feed.id)
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
            ''', (feed.url, feed.name, feed.frequency, feed.last_run)
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
        conn.row_factory = dict_factory
        subscriptions = get_subscriptions(conn, True)
        conn.close()
        return subscriptions


def get_settings_value(conn, key, a_type=int):
    conn.row_factory = dict_factory
    c = conn.cursor()

    c.execute('SELECT val FROM SETTINGS WHERE id=?', (str(key),))
    try:

        db_mod = c.fetchone().get('val')

        if db_mod is None:
            return None
        else:
            return a_type(db_mod)
    except:
        return None


def get_feeds(conn):
    feeds = {}

    c = conn.cursor()

    c.execute(
        '''
            SELECT id, url, name, frequency, last_pub FROM Feeds;
        '''
    )
    for feed in c.fetchall():
        # id, url, name="new feed", frequency=300, last_pub
        new_feed = Feed(**feed)

        feeds['Feed-' + str(feed['id'])] = new_feed
        logging.debug('Added Feed-' + str(feed['id']))

    return feeds


def get_subscriptions(conn, all_subs=False):

    subscriptions = {}

    c = conn.cursor()

    if all_subs is True:
        c.execute(
            '''
              SELECT * FROM Subscriptions;
            '''
        )
    else:
        c.execute(
            '''
              SELECT * FROM Subscriptions WHERE enabled = 1;
            '''
        )
    for sub in c.fetchall():

        new_sub = Subscription(**sub)

        subscriptions['Subscription-' + str(sub['id'])] = new_sub

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
        episodes.append(ep['episode'])

    return episodes


def get_torrents(conn):
    d = conn.cursor()
    d.execute(
        '''
            SELECT link, status, subscriptionid, folder, file, final_location, status_time FROM Torrents
        '''
    )
    torrents = {}
    for tor in d.fetchall():
        a_torrent = Torrent(**tor)
        a_torrent.final_location = tor['final_location']
        a_torrent.status_time = int(tor['status_time'])
        torrents[a_torrent.folder] = a_torrent

    return torrents


def get_db_version(conn):
    conn.row_factory = dict_factory
    d = conn.cursor()
    d.execute(
        '''
            PRAGMA table_info('Settings')
        '''
    )
    columns = d.fetchall()
    if len(columns) == 2:
        if columns[0]['name'] == 'name' and columns[1]['name'] == 'version':
            # 1 and 2
            d.execute("SELECT version FROM SETTINGS WHERE name='DB_VERSION'")
            db_mod = d.fetchone()
            if db_mod is None or db_mod.get('version') is None:
                return 1
            else:
                return 2

        elif columns[0]['name'] == 'id' and columns[1]['name'] == 'val':
            # 3 and up
            curr_version = get_settings_value(conn, 'DB_VERSION', int)
            if curr_version is not None:
                return curr_version
            else:
                raise sqlite3.DataError("Current version unknown")


def verify_sql_change(cursor, get_one, should_equal, table_name, ret_object=False):
    the_value = None
    reason = ""
    try:
        cursor.execute(get_one)
        the_value = cursor.fetchone()[0]
    except sqlite3.OperationalError as op_error:
        reason = str(op_error.message) + '\r\n'

    if the_value == should_equal:
        logging.info("Verified changes to table " + str(table_name))
        if ret_object is True:
            return {"ret": True, "info": "Success"}
        return True

    elif the_value is None:
        cursor.execute("PRAGMA table_info(\'" + str(table_name) + "\')")
        rows = cursor.fetchall()
        if rows is None or len(rows) == 0:
            reason += "Failed to create database table " + str(table_name)
        else:
            reason = "Failed because of syntax in change for table " + str(table_name) + \
                     "\r\nColumnId\tName\tType\tdefault\tisPrimary\r\n\t"
            for row in rows:
                reason += "\t".join([str(col) for col in row])
                reason += "\r\n\t"
    else:
        reason = "Failed because value: " + str(the_value) + " != " + str(should_equal)

    if ret_object is True:
        return {"ret": False, "info": reason}
    else:
        logging.error(reason)
    return False


# http://stackoverflow.com/a/3300514
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
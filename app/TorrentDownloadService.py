__author__ = 'Dirrk'

import logging
import time
import shutil

from lib.DataStore import DataStore
import app.plex.plex as plex
from app.torrent.Torrent import Torrent
import os
import app.settings as settings


class TorrentService:
    def __init__(self):
        self.db = DataStore()
        self._continue = False

    def install(self):

        if os.name == 'nt' and os.path.exists(settings.SEVEN_ZIP) is False:
            raise Exception("7zip was not configured correctly please check your settings")

        if create_folder(settings.TORRENT_DIRECTORY) is True and create_folder(
                settings.DOWNLOAD_DIRECTORY) is True and create_folder(settings.COMPLETE_DIRECTORY) is True:
            self.db.create()
        else:
            raise Exception("Could not create torrent folders are they configured correctly?")

    def upgrade(self):

        shutil.copyfile(self.db.__db_file__, self.db.__db_file__ + '.bak')

        if self.db.upgrade() is True:
            os.remove(self.db.__db_file__ + '.bak')
        else:
            raise IndexError("Failed to upgrade database, backed up current database to location:\r\n"
                             + self.db.__db_file__ + '.bak')

    def start(self):

        # Open data file and parse data
        self.db.load()

        # Merge Plex Shows with active
        if settings.USE_PLEX is True:
            different_subs = plex.PlexHelper.find_new_subs(self.db.get_all_subscriptions())

            for sub in different_subs:
                if sub.id != 0:
                    self.db.update_subscription(sub)
                else:
                    feeds = [self.db.feeds[key] for key in self.db.feeds.keys()]

                    if len(feeds) > 0:
                        sub.feedId = feeds[0].id

                    self.db.add_subscription(sub)

        self._continue = True
        try:

            self._loop()
        except Exception as e:
            logging.exception(e)
            logging.warn("Restarting Torrent Service in 30 seconds")
            time.sleep(30)
            self.start()

    def _loop(self):

        while self._continue is True:

            self.db.reload()

            for feed_id in self.db.feeds:
                feed = self.db.feeds[feed_id]
                self._loop_feed(feed)

            for t_id in self.db.torrents:
                torrent = self.db.torrents[t_id]
                if torrent.check_status(self.db.db_callback_by_id) is False:
                    logging.warn(torrent.to_string())
                    self.db.update_torrent(torrent)

            time.sleep(15)

    def _loop_feed(self, feed):

        if feed.update_cycle() is True:
            items = feed.fetch_items()

            for key in self.db.subscriptions:
                sub = self.db.subscriptions[key]
                if sub.feedId == feed.id:
                    self._loop_subs(sub, items)
            self.db.update_feed(feed)

    def _loop_subs(self, sub, items=[]):

        matched = sub.match(items)
        if matched is not None and len(matched) > 0:
            for match in matched:
                logging.info("Found matches:" + str(match.title))

                a_torrent = Torrent(match.link)
                a_torrent.subscriptionId = sub.id
                a_torrent.episode = match.episodes[0]
                if settings.USE_PLEX is True:
                    a_torrent.final_location = plex.PlexHelper.find_location(sub.plex_id,
                                                                             match.episodes[0])
                if a_torrent.download() is True:
                    logging.info("Downloaded torrent successfully")
                    self.db.add_torrent(a_torrent)
                else:
                    logging.error("Torrent failed to download")

        self.db.update_subscription(sub)


def create_folder(folder, attempts=None):
    if attempts is None:
        folder = os.path.abspath(folder)
        attempts = len(folder.split(os.path.sep))

        if os.path.exists(folder):
            return True

    if attempts > 1:

        if os.path.exists(folder):
            return True
        else:
            test_folder = os.path.dirname(folder)
            if create_folder(test_folder, attempts - 1):
                os.mkdir(folder)
                return True
            else:
                return False
    else:
        return False



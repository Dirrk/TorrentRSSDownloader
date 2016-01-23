__author__ = 'Dirrk'

import logging
import time
import shutil
import math

import app.gmail.gmail as email
from lib.DataStore import DataStore
import app.plex.plex as plex
from app.torrent.Torrent import Torrent
import os
import app.settings as settings


class TorrentService:
    def __init__(self):
        self.db = DataStore()
        self._continue = False

    def setup(self):

        if not os.path.exists(settings.DATA_FILE):
            self.db.create()

        self.db.load()

        create_folder(settings.TORRENT_DIRECTORY)
        create_folder(settings.INCOMING_DIRECTORY)
        create_folder(settings.DOWNLOAD_DIRECTORY)
        create_folder(settings.COMPLETE_DIRECTORY)

        if os.name == 'nt' and os.path.exists(settings.SEVEN_ZIP) is False:
            logging.warn("7zip was not configured correctly, you will not be able to extract archived torrents without it")
        elif not (os.path.isfile('/usr/bin/unrar') and os.path.isfile('/bin/unrar')):
            logging.warn("unrar was not configured correctly, you will not be able to extract archived torrents without it")

    def start(self):
        logging.debug("TorrentDownloadService start")
        # Open data file and parse data
        self.db.load()

        # Merge Plex Shows with active
        if settings.USE_PLEX is True:
            different_subs = plex.PlexHelper.find_new_subs(self.db.get_all_subscriptions())
            logging.info("Downloaded new subs from plex")
            for sub in different_subs:
                if sub.id != 0:
                    self.db.update_subscription(sub)
                else:
                    feeds = [self.db.feeds[key] for key in self.db.feeds.keys()]

                    if len(feeds) > 0:
                        sub.feedId = feeds[0].id

                    self.db.add_subscription(sub)
                    logging.info("Added subscription to " + sub.name)

        self._continue = True
        try:

            self._loop()
        except Exception as e:
            logging.exception(e)
            logging.warn("Restarting Torrent Service in 30 seconds")
            time.sleep(30)
            exit()

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

            self._loop_send_email()
            time.sleep(15)

    def _loop_send_email(self):
        # Accidentally merged into master before this was ready
        if self.db.get_setting('EMAIL_ENABLED', bool) is not True:
            return
        current_ts = int(math.floor(time.time()))
        last_ts = self.db.get_setting('LAST_REPORT', int)
        email_frequency = self.db.get_setting('EMAIL_FREQUENCY', int)
        if last_ts is None:
            last_ts = 0
            self.db.set_setting('LAST_REPORT', int(last_ts))
        if email_frequency is None:
            email_frequency = 3
            self.db.set_setting('EMAIL_FREQUENCY', email_frequency)

        email_frequency *= 86400

        if current_ts - last_ts > email_frequency:
            email.send_email_report(self.db.get_all_torrents(last_ts), self.db.db_callback_by_id)
            self.db.set_setting('LAST_REPORT', int(math.floor(current_ts)))

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



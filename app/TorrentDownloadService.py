__author__ = 'Dirrk'

import logging

log = logging.getLogger()
from lib.DataStore import DataStore
import app.plex.plex as plex
from app.torrent.Torrent import Torrent
import time


class TorrentService:
    def __init__(self):
        self.db = DataStore()
        self._continue = False

    def start(self):

        # Open data file and parse data
        self.db.load()

        # Merge Plex Shows with active
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
        self._loop()

    def _loop(self):

        while self._continue is True:

            self.db.reload()

            for feed_id in self.db.feeds:

                feed = self.db.feeds[feed_id]
                if feed.update_cycle() is True:
                    items = feed.fetch_items()

                    for key in self.db.subscriptions:
                        sub = self.db.subscriptions[key]
                        if sub.feedId == feed.id:
                            matched = sub.match(items)
                            if matched is not None and len(matched) > 0:
                                for match in matched:
                                    logging.debug("Found matches:" + str(match.title))

                                    a_torrent = Torrent(match.link)
                                    a_torrent.subscriptionId = sub.id
                                    a_torrent.final_location = plex.PlexHelper.find_location(sub.plex_id,
                                                                                             match.episodes[0])
                                    if a_torrent.download() is True:
                                        self.db.add_torrent(a_torrent)
                                    else:
                                        logging.error("Torrent failed to download")

                            self.db.update_subscription(sub)
                    self.db.update_feed(feed)

            for t_id in self.db.torrents:
                torrent = self.db.torrents[t_id]
                if torrent.check_status() is False:
                    logging.warn(torrent.to_string())
                    self.db.update_torrent(torrent)

            time.sleep(15)
__author__ = 'Dirrk'

import logging

log = logging.getLogger()
from lib.DataStore import DataStore
import os.path as path
import cPickle


class TorrentService:
    def __init__(self, config):
        self.db = None
        self.config = config
        log.info("Starting torrent download service debug=%s" % config.get('debug'))

    def start(self):

        # Open data file and parse data
        self.get_saved_data()

        for feed in self.db.feeds:
            # Fetch feed and give handler for getting matches
            feed.fetch(self.db, self.match_handler)

    def get_saved_data(self):

        log.debug("Inside get saved data")

        if self.config.get("dataFile") is None:
            self.config.set("dataFile", "./data/torrent.db")
            log.debug("Data file was not available")

        filename = self.config.get("dataFile")
        if path.exists(filename):
            log.debug("Opening file: %s" % filename)
            f = open(filename, 'r')
            up = cPickle.Unpickler(f)
            self.db = up.load()
            f.close()
        else:
            self.db = DataStore()
            log.debug("Opening file: %s" % filename)
            f = open(filename, 'w')
            p = cPickle.Pickler(f)
            p.dump(self.db)
            f.close()
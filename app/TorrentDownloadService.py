__author__ = 'Dirrk'

import logging

import app.settings as settings

log = logging.getLogger()
from lib.DataStore import DataStore


class TorrentService:
    def __init__(self):
        self.db = None
        log.info("Starting torrent download service debug=%s" % settings.__DEBUG__)

    def start(self):

        # Open data file and parse data
        self.db = DataStore()
        self.db.load()

        # Loop through feeds sleeping for 30 seconds in between
__author__ = 'Dirrk'

import logging

import requests
from app.torrent.bencode import torrent_file_to_dictionary as infoParser
import re
import os.path as path
import app.settings as settings


class Torrent:
    def __init__(self, link, status=0, file=None, folder="", subscription_id=0):
        self.link = link
        self.status = status  # 0 - Nothing, 1 - Downloaded torrent file, 2 - Download complete, 3 - organized
        self.file = file
        self.folder = folder
        self.subscriptionId = subscription_id

        if self.file is None:
            my_file = re.split('/', self.link)
            my_file = re.split('\?', my_file[-1])

            t_directory = settings.TORRENT_DIRECTORY

            if my_file is not None:
                self.file = path.join(t_directory, my_file[0])
            else:
                self.file = path.join(t_directory, 'temporary.torrent')

    def download(self):
        try:
            req = requests.get(self.link)
            with open(self.file, "wb") as torrent:
                torrent.write(req.content)

            torrent_info = infoParser(self.file)

            self.folder = torrent_info['name']
            self.status = 1  # 1 = Downloaded torrent file
            return True

        except Exception as e:
            logging.exception(e)
            return False

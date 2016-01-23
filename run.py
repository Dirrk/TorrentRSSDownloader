__author__ = 'Dirrk'

import argparse
import sys
import logging

import os
import app.settings as settings
from app.TorrentDownloadService import TorrentService

__version__ = '1.3.0'


# https://docs.python.org/2/library/logging.html#levels
def main(args):
    parser = argparse.ArgumentParser(description="Monitors RSS Feeds and downloads torrents")
    parser.add_argument('-d', '--db', type=str, default=settings.DATA_FILE,
                        help="location of the database to use")
    # Parse config from arguments
    my_args = parser.parse_args(args)
    db_file = my_args.db

    settings.DATA_FILE = db_file

    # Setup Logging
    root = logging.getLogger()
    root.setLevel(settings.LOG_LEVEL)

    # Create streaming handler to stdout
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(settings.LOG_LEVEL)

    # Define Format
    lf = logging.Formatter('%(asctime)s %(levelname)s %(module)s %(funcName)s %(process)d:%(thread)d %(message)s')
    ch.setFormatter(lf)

    # Add the handlers to the root logger
    root.addHandler(ch)

    ts = TorrentService()

    # Start application
    logging.info("Starting TorrentService")
    logging.info("Settings:"
                 "\nDATA_FILE: " + settings.DATA_FILE +
                 "\nTORRENT_DIRECTORY: " + settings.TORRENT_DIRECTORY +
                 "\nINCOMING_DIRECTORY: " + settings.INCOMING_DIRECTORY +
                 "\nDOWNLOAD_DIRECTORY: " + settings.DOWNLOAD_DIRECTORY +
                 "\nCOMPLETE_DIRECTORY: " + settings.COMPLETE_DIRECTORY)

    ts.setup()
    ts.start()


if __name__ == "__main__":
    main(sys.argv[1:])

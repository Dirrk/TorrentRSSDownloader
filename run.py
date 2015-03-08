__author__ = 'Dirrk'

import argparse
import sys
import logging

import app.settings as settings
from app.TorrentDownloadService import TorrentService


__version__ = '1.2.0'


# https://docs.python.org/2/library/logging.html#levels
def main(args):
    parser = argparse.ArgumentParser(description="Monitors RSS Feeds and downloads torrents")
    parser.add_argument('-d', '--database', type=str, default=settings.DATA_FILE,
                        help="location of the database to use")
    parser.add_argument('-e', '--env', default='', type=str, choices=['Dev', 'Stage', 'Production'])
    parser.add_argument('--upgrade', action='store_true')
    parser.add_argument('--install', action='store_true')

    # Parse config from arguments
    my_args = parser.parse_args(args)
    db_file = my_args.database
    env = my_args.env

    settings.apply_settings(env)
    settings.DATA_FILE = db_file

    # Setup Logging
    root = logging.getLogger()
    root.setLevel(settings.LOG_LEVEL)

    # Create streaming handler to stdout
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(settings.LOG_LEVEL)

    # Define Format
    ch.setFormatter(
        logging.Formatter('%(asctime)s %(levelname)s %(module)s %(funcName)s %(process)d:%(thread)d %(message)s'))

    # Add the stream handler to the root logger
    root.addHandler(ch)

    ts = TorrentService()
    if my_args.install is True:
        ts.install()

    elif my_args.upgrade is True:
        ts.upgrade()

    # Start application
    ts.start()


if __name__ == "__main__":
    main(sys.argv[1:])

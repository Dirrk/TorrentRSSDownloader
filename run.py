__author__ = 'Dirrk'

import argparse
import sys
import logging

import app.settings as settings
from app.TorrentDownloadService import TorrentService



# https://docs.python.org/2/library/logging.html#levels
def main(args):
    parser = argparse.ArgumentParser(description="Monitors RSS Feeds and downloads torrents")
    parser.add_argument('-c', '--config', nargs='?', type=str, default="./config.json",
                        help="location of the config to use")
    # Parse config from arguments
    config_file = parser.parse_args(args).config

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

    root.info("Starting application with config %s", config_file)

    # Start application
    TorrentService().start()


if __name__ == "__main__":
    main(sys.argv[1:])

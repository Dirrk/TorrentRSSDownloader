__author__ = 'Dirrk'

import argparse
import sys
import logging

from lib.config import conf
import app.TorrentDownloadService as TorrentDownloadService
from lib.jsof import reader as parse



# https://docs.python.org/2/library/logging.html#levels
def main(args):
    parser = argparse.ArgumentParser(description="Monitors RSS Feeds and downloads torrents")
    parser.add_argument('-c', '--config', nargs='?', type=str, default="./config.json",
                        help="location of the config to use")
    # Parse config from arguments
    config_file = parser.parse_args(args).config

    # Setup Logging
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # Create streaming handler to stdout
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)

    # Define Format
    ch.setFormatter(
        logging.Formatter('%(asctime)s %(levelname)s %(module)s %(funcName)s %(process)d:%(thread)d %(message)s'))

    # Add the stream handler to the root logger
    root.addHandler(ch)

    root.info("Starting application with config %s", config_file)

    # Parse config into object
    config = conf(parse(config_file))

    # Change log level
    if config.get('log_level') is not None:
        root.setLevel(config.get('log_level'))

    # Start application
    TorrentDownloadService(config).start()


if __name__ == "__main__":
    main(sys.argv[1:])

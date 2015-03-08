__author__ = 'Dirrk'

import os


__ENV__ = os.environ.get('ENV')
LOG_LEVEL = 10
DATA_FILE = "C:\\Users\\derek_000\\PycharmProjects\\TorrentDownloader\\data\\dev-torrents.db"
TORRENT_DIRECTORY = "F:\\test-area\\dev\\monitor"
DOWNLOAD_DIRECTORY = "F:\\test-area\\dev\\downloading"
COMPLETE_DIRECTORY = "F:\\test-area\\dev\\complete"
SEVEN_ZIP = "C:\\7zip\\7z.exe"
PLEX_HOST = 'localhost:32400'
EMAIL_DATA = {
    "TO": [str(os.environ.get('SEND_TO'))],
    "ACCOUNT": {
        "USER": str(os.environ.get('EMAIL_ACCOUNT_USER')),
        "PASS": str(os.environ.get('EMAIL_ACCOUNT_PASS')),
    },
    "FREQUENCY": 7
}
TORRENT_SHARE_TIME = 14
FEED = ("http://www.iptorrents.com/torrents/rss?download;l66;l65;l5;l4;u=1216603;tp=" + str(os.environ.get('TOKEN')),)
PLEX_TV_SECTION = 2


def apply_settings(env='Dev'):
    global LOG_LEVEL, DATA_FILE, TORRENT_DIRECTORY, DOWNLOAD_DIRECTORY, COMPLETE_DIRECTORY

    if env == 'Production':
        LOG_LEVEL = 20
        DATA_FILE = "C:\\Users\\derek_000\\PycharmProjects\\TorrentDownloader\\data\\torrents.db"
        TORRENT_DIRECTORY = "F:\\Incoming\\monitor"
        DOWNLOAD_DIRECTORY = "F:\\Incoming"
        COMPLETE_DIRECTORY = "Z:\\Completed"

        print "Production"

    elif env == 'Stage':
        DATA_FILE = "C:\\Users\\derek_000\\PycharmProjects\\TorrentDownloader\\data\\stage-torrents.db"
        TORRENT_DIRECTORY = "F:\\test-area\\stage\\monitor"
        DOWNLOAD_DIRECTORY = "F:\\test-area\\stage\\downloading"
        COMPLETE_DIRECTORY = "F:\\test-area\\stage\\complete"
        print "Stage"


apply_settings(__ENV__)
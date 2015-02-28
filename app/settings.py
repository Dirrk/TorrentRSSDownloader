__author__ = 'Dirrk'

import os


__ENV__ = os.environ.get('ENV')

__DEBUG__ = True
LOG_LEVEL = 10
DATA_FILE = "C:\\Users\\derek_000\\PycharmProjects\\TorrentDownloader\\data\\torrents.db"
TORRENT_DIRECTORY = "F:\\test-area\\dev\\monitor"
DOWNLOAD_DIRECTORY = "F:\\test-area\\dev\\downloading"
COMPLETE_DIRECTORY = "F:\\test-area\\dev\\complete"
SEVEN_ZIP = "C:\\7zip\\7z.exe"
PLEX_HOST = 'localhost:32400'
FEED = ("http://www.iptorrents.com/torrents/rss?download;l66;l65;l5;l4;u=1216603;tp=" + os.environ.get('TOKEN'),)
PLEX_TV_SECTION = 2


if __ENV__ == 'Production':
    __DEBUG__ = False
    DATA_FILE = "C:\\Users\\derek_000\\PycharmProjects\\TorrentDownloader\\data\\torrents.db"
    TORRENT_DIRECTORY = "F:\\Incoming\\monitor"
    DOWNLOAD_DIRECTORY = "F:\\Incoming"
    COMPLETE_DIRECTORY = "Z:\\Completed"

    print "Production"

elif __ENV__ == 'Stage':
    TORRENT_DIRECTORY = "F:\\test-area\\stage\\monitor"
    DOWNLOAD_DIRECTORY = "F:\\test-area\\stage\\downloading"
    COMPLETE_DIRECTORY = "F:\\test-area\\stage\\complete"
    print "Stage"






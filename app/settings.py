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
PLEX_HOST = '192.168.137.1:32400'

if __ENV__ == 'Production':
    __DEBUG__ = False
    print "Production"

elif __ENV__ == 'Stage':
    TORRENT_DIRECTORY = "F:\\test-area\\stage\\monitor"
    DOWNLOAD_DIRECTORY = "F:\\test-area\\stage\\downloading"
    COMPLETE_DIRECTORY = "F:\\test-area\\stage\\complete"
    print "Stage"






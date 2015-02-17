__author__ = 'Dirrk'

import os


__ENV__ = os.environ.get('ENV')

__DEBUG__ = True
LOG_LEVEL = 10
DATA_FILE = "C:\\Users\\derek_000\\PycharmProjects\\TorrentDownloader\\data\\torrents.db"
TORRENT_DIRECTORY = "F:\\Incoming\\monitor"

if __ENV__ == 'Production':
    __DEBUG__ = False
    print "Production"

elif __ENV__ == 'Stage':
    print "Stage"






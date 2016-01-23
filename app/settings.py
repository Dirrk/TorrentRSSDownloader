__author__ = 'Derek Rada'

# Normal python logging levels https://docs.python.org/2/library/logging.html#levels
LOG_LEVEL = 20

# Required for windows
SEVEN_ZIP = ""

# Plex
USE_PLEX = False

# Your local plex server
PLEX_HOST = 'localhost:32400'

# You must pick your tv section from the list to get the list open your browser to your plex_host with
# uri /library/sections and choose the "key" it will be a string of a number that has the type show
# in example curl http://localhost:32400/library/sections
PLEX_TV_SECTION = 1


# Email
# This can be setup later or not at all and currently only supports gmail
EMAIL_ENABLED = False

# Who should the email go to?
EMAIL_TO = ""

# The account sending the email
EMAIL_ACCOUNT_USER = ""
EMAIL_ACCOUNT_PASS = ""
EMAIL_ACCOUNT_PORT = 587
EMAIL_ACCOUNT_HOST = "smtp.gmail.com"

# How frequently should the service send email updates
EMAIL_FREQUENCY = 7


# Torrent Cleanup
TORRENT_SHARE_TIME = 14
CLEAN_UP_TORRENTS = TORRENT_SHARE_TIME

# Files / Folders
DATA_FILE = "./torrents.db"

TORRENT_DIRECTORY = "./data/torrent"
INCOMING_DIRECTORY = "./data/incoming"
DOWNLOAD_DIRECTORY = "./data/download"
COMPLETE_DIRECTORY = "./data/complete"

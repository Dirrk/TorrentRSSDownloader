__author__ = 'Dirrk'

import logging
import shutil
import subprocess
import time
import math

from app.rss.Item import parse_episode as episode_parser
import requests
from app.torrent.bencode import torrent_file_to_dictionary as infoParser
import re
import os
import app.settings as settings
from app.plex.plex import PlexHelper


logging.getLogger('requests').setLevel(logging.WARNING)
DAY_IN_SECONDS = 86400


class Torrent:
    def __init__(self, link, status=0, file=None, folder="", subscriptionid=0, final_location=None, status_time=None,
                 episode=''):
        self.link = link
        self.status = status  # 0 - Nothing, 1 - Downloaded torrent file, 2 - Downloading, 3 - Download complete, 4 - organized 5 - failed
        self.file = file
        self.folder = folder  # Folder that files will be contained in
        self.subscriptionId = subscriptionid  # Local Subscription Id
        self.final_location = final_location  # Location we are going to move the file to
        self.episode = episode  # the episode that was found

        if status_time is None or status_time == 0:
            self.status_time = math.ceil(time.time())
        else:
            self.status_time = status_time

        if self.file is None:
            my_file = re.split('/', self.link)
            my_file = re.split('\?', my_file[-1])

            t_directory = settings.TORRENT_DIRECTORY

            if my_file is not None:
                self.file = os.path.join(t_directory, my_file[0])
            else:
                self.file = os.path.join(t_directory, 'temporary.torrent')

    def download(self):
        try:
            req = requests.get(self.link)
            with open(self.file, "wb") as torrent:
                torrent.write(req.content)

            torrent_info = infoParser(self.file)

            self.folder = torrent_info['name']
            self.status = TORRENT_STATES["TORRENT_RETRIEVED"]  # 1 = Downloaded torrent file
            return True

        except Exception as e:
            logging.error("File failed to download:" + str(self.link))
            logging.exception(e)
            self.status = TORRENT_STATES["ERROR"]
            return False

    def check_status(self, callback=None):

        changed = (self.status + 0)  # Not needed but I do it

        if (self.status == TORRENT_STATES["ERROR"] or self.status == TORRENT_STATES["NEW"]) and os.path.exists(
                self.file):
            self.status = TORRENT_STATES["TORRENT_RETRIEVED"]

        elif self.status <= TORRENT_STATES["TORRENT_RETRIEVED"] and os.path.exists(
                os.path.join(settings.DOWNLOAD_DIRECTORY, self.folder)):
            self.status = TORRENT_STATES["DOWNLOADING"]

        elif self.status <= TORRENT_STATES["DOWNLOADING"] and os.path.exists(
                os.path.join(settings.COMPLETE_DIRECTORY, self.folder)) and not os.path.exists(
                os.path.join(settings.DOWNLOAD_DIRECTORY, self.folder)):
            self.status = TORRENT_STATES["DOWNLOADED"]

        if self.status == TORRENT_STATES["DOWNLOADED"]:
            self._organize()

        elif self.status == TORRENT_STATES["COMPLETE"] and self.status_time == 0:
            if os.path.exists(os.path.join(settings.COMPLETE_DIRECTORY, self.folder)) is True:
                self.status_time = int(
                    math.ceil(os.path.getmtime(os.path.join(settings.COMPLETE_DIRECTORY, self.folder))))
                return False
            elif callback is not None and self.episode != '':
                sub = callback('sub', self.subscriptionId)
                if sub is not None and sub.plex_id > 0:
                    plex_episode = PlexHelper.get_episode_by_string(sub.plex_id, self.episode)
                    if plex_episode is not None:
                        self.status_time = plex_episode.addedAt
                        return False
            elif callback is not None and self.episode == '':
                episodes = episode_parser(self.file)
                if len(episodes) > 0:
                    sub = callback('sub', self.subscriptionId)
                    if sub is not None and sub.plex_id > 0:
                        plex_episode = PlexHelper.get_episode_by_string(sub.plex_id, episodes[-1])
                        self.episode = episodes[-1]
                        if plex_episode is not None:
                            self.status_time = plex_episode.addedAt
                        return False

        elif self.status == TORRENT_STATES["COMPLETE"] and self.status_time - math.ceil(time.time()) >= DAY_IN_SECONDS \
                * settings.CLEAN_UP_TORRENTS:
            self.status = TORRENT_STATES["FINISHED"]

        elif self.status == TORRENT_STATES["COMPLETE"] and not os.path.exists(
                os.path.join(settings.COMPLETE_DIRECTORY, self.folder)):  # Completed but deleted
            self.status = TORRENT_STATES["FINISHED"]

        elif self.status == TORRENT_STATES["FATAL"] and ((not os.path.exists(
                os.path.join(settings.COMPLETE_DIRECTORY, self.folder)) or self.status_time - math.ceil(time.time()) >=
                DAY_IN_SECONDS * settings.CLEAN_UP_TORRENTS)):
            self.status = TORRENT_STATES["FINISHED"]

        has_changed = (changed - self.status) == 0
        if has_changed is True:
            self.status_time = int(math.ceil(time.time()))

        return has_changed

    def _organize(self):

        self.status = TORRENT_STATES["COMPLETE"]

        if self.final_location is None or self.folder == "":
            return

        working_dir = os.path.join(settings.COMPLETE_DIRECTORY, self.folder)

        # Handle where the folder is actually not a folder but the only file that downloaded should be rare
        if not os.path.isdir(working_dir):
            try:
                shutil.copy(working_dir, self.final_location)
            except Exception as e:
                self.status = TORRENT_STATES["FATAL"]
                logging.exception(e)
                logging.error("Torrent failed to move ", working_dir, "to", self.final_location)
            finally:
                return

        # Retrieve files in destination folder
        files = []
        for (dirpath, dirnames, filenames) in os.walk(working_dir):
            for file in filenames:
                files.append(os.path.join(dirpath, file))
            break

        # Handle where there is just one large file
        if len(files) == 1:
            if not os.path.exists(self.final_location):
                os.mkdir(self.final_location)

            shutil.copy(files[0], self.final_location)
            return

        # Mark .rar or .000 or .zip or .tar
        match_archive = None
        match_video = None
        match_video_size = 0
        search_archives = re.compile('[\.](rar|001|zip|tar)$', re.IGNORECASE)
        search_movies = re.compile('[\.](mkv|mp4|avi|m4v|mpeg|mpg|vob|wmv)$', re.IGNORECASE)
        ignore_files = re.compile('(.*sample.*|[\.](nfo|sfv|r[0-9][0-9])$)', re.IGNORECASE)

        for file in files:
            arch = search_archives.search(file)
            if arch is not None:
                match_archive = file
                break

            mov = search_movies.search(file)
            if mov is not None and ignore_files.search(file) is None and os.path.getsize(file) > match_video_size:
                match_video = file
                match_video_size = os.path.getsize(file)

        logging.info("Match Archive:" + str(match_archive))
        logging.info("Match Videos:" + str(match_video))

        if match_archive is None:
            if match_video is None:
                logging.debug("Couldn't find match")
                return
            if not os.path.exists(self.final_location):
                os.mkdir(self.final_location)

            shutil.copy(match_video, self.final_location)
            return

        if extract_file(file, self.final_location) is not True:
            self.status = TORRENT_STATES["FATAL"]
        else:
            self.status = TORRENT_STATES["COMPLETE"]

    def to_string(self):
        return "Torrent:", self.folder, "in status:", self.status_to_string()

    def status_to_string(self):
        return [key for key in TORRENT_STATES if TORRENT_STATES[key] == self.status][0]

TORRENT_STATES = {
    "NEW": 0,
    "TORRENT_RETRIEVED": 1,
    "DOWNLOADING": 2,
    "DOWNLOADED": 3,
    "COMPLETE": 4,
    "ERROR": 5,
    "FATAL": 6,
    "FINISHED": 7
}


def extract_file(archive, dst):
    # Windows use 7zip
    if os.name == 'nt':
        if settings.SEVEN_ZIP is not None:
            if not os.path.exists(dst):
                os.mkdir(dst)
            # C:\7zip\7z.exe e -o"F:\test-area\dev\Plex_Area\Drive A\TV\Show ABC\S1" "F:\test-area\dev\complete\My.Favorite.Show.S01E02\Laggies.2014.LIMITED.720p.BRRiP.X264.Ac3.CrEwSaDe.Sample.zip.001"
            cmd = settings.SEVEN_ZIP, '-y', 'x', '-o' + dst, archive
            logging.info(str(cmd))
            try:
                subprocess.check_call(cmd)
                return True
            except subprocess.CalledProcessError as e:
                logging.exception(e)
                logging.error("Failed to extract file: " + archive)
                return False

        else:
            logging.exception("7zip value not set")

    # lx use unrar
    else:
        # run unrar
        return True


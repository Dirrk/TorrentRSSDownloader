__author__ = 'Dirrk'

import logging
import shutil
import subprocess

import requests
from app.torrent.bencode import torrent_file_to_dictionary as infoParser
import re
import os
import app.settings as settings


class Torrent:
    def __init__(self, link, status=0, file=None, folder="", subscription_id=0):
        self.link = link
        self.status = status  # 0 - Nothing, 1 - Downloaded torrent file, 2 - Downloading, 3 - Download complete, 4 - organized 5 - failed
        self.file = file
        self.folder = folder  # Folder that files will be contained in
        self.subscriptionId = subscription_id
        self.final_location = None

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
            logging.error("File failed to download: %s", self.link)
            logging.exception(e)
            self.status = TORRENT_STATES["ERROR"]
            return False

    def check_status(self):

        changed = (self.status + 0)  # Not needed but I do it

        if (self.status == TORRENT_STATES["ERROR"] or self.status == TORRENT_STATES["NEW"]) and os.path.exists(
                self.file):
            self.status = TORRENT_STATES["TORRENT_RETRIEVED"]

        elif self.status == TORRENT_STATES["TORRENT_RETRIEVED"] and os.path.exists(
                os.path.join(settings.DOWNLOAD_DIRECTORY, self.folder)):
            self.status = TORRENT_STATES["DOWNLOADING"]

        elif self.status == TORRENT_STATES["DOWNLOADING"] and os.path.exists(
                os.path.join(settings.COMPLETE_DIRECTORY, self.folder)):
            self.status = TORRENT_STATES["DOWNLOADED"]

        if self.status == TORRENT_STATES["DOWNLOADED"]:
            self.organize()

        print "Status: ", changed
        return (changed - self.status) == 0

    def organize(self):

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
                print "Torrent failed to move ", working_dir, "to", self.final_location
            finally:
                return

        # Retrieve files in destination folder
        files = []
        for (dirpath, dirnames, filenames) in os.walk(working_dir):
            for file in filenames:
                files.append(dirpath + file)
            break

        # Handle where there is just one large file
        if len(files) == 1:
            shutil.copy(files[0], self.final_location)
            return

        # Mark .rar or .000 or .zip or .tar
        match_archive = None
        match_video = None
        match_video_size = 0
        search_archives = re.compile('[\.](rar|000|zip|tar)$', re.IGNORECASE)
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

        print "Match Archive:", match_archive
        print "Match Videos:", match_video

        if match_archive is None:
            shutil.copy(match_video, self.final_location)
            return

        if extract_file(file, self.final_location) is True:
            self.status = TORRENT_STATES["FATAL"]


TORRENT_STATES = {
    "NEW": 0,
    "TORRENT_RETRIEVED": 1,
    "DOWNLOADING": 2,
    "DOWNLOADED": 3,
    "COMPLETE": 4,
    "ERROR": 5,
    "FATAL": 6
}


def extract_file(archive, dst):
    # Windows use 7zip
    if os.name == 'nt':
        if settings.SEVEN_ZIP is not None:
            cmd = settings.SEVEN_ZIP, 'e', '-o"' + dst + '"', '"' + archive + '"'
            try:
                subprocess.call(cmd)
                return True
            except subprocess.CalledProcessError as e:
                print e
                logging.exception(e)
                print "Failed to extract file"
                return False

        else:
            logging.exception("7zip value not set")

    # lx use unrar
    else:
        # run unrar
        return True


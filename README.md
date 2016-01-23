# TorrentRSSDownloader
TorrentRSSDownloader

This is used to download torrents from an rss feed(s), verify against plex and then organize the media when the torrent completes.

## How to install:

* Install unrar (linux/mac) or 7zip (windows)
* Install python (I have tested up to v2.7)
* Download this repository
* Modify the settings.py to contain your settings (defaults will be setup for you)
* Install and setup torrent client (see proper setup below)

## How to setup your torrent client:

* You will have already setup/define folders(incoming/download/completed/torrents) to use in your settings.py
* Choose to have your torrent client automatically add .torrent files from the "incoming" folder
* Choose to have your torrent client copy the .torrent files to the "torrents" folder and if applicable delete the copy on remove
* Choose to have your torrent client download files to the "download" folder
* Choose to have your torrent client move completed files to the "completed" folder
Please note if you did not setup the directories ahead of time they will be configured to be in the temp folder

## How to configure your subscriptions / feeds
* Currently there is no UI, however you can easily modify and do anything with the data by simply downloading a SQL Lite browser
* If anyone would like to contribute to this please feel free
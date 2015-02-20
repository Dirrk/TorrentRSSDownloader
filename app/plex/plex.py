__author__ = 'Dirrk'

import xml.etree.ElementTree as ET

import requests
import app.settings as settings
import re
import os.path as path


class ApiHelper():
    def __init__(self, host=None):
        if host is None and settings.PLEX_HOST is None:
            raise Exception("Provide Host or define PLEX_HOST in settings.py")
        elif host is None:
            self.__host__ = settings.PLEX_HOST
        else:
            self.__host__ = host

    def get_sections(self):
        return self.plex_api_call('sections')

    def get_show_by_id(self, show_id):
        shows = self.plex_api_call('metadata/' + str(show_id))
        if shows is not None and len(shows) >= 1:
            return Show(shows[0])
        else:
            return None

    def get_all_shows(self, section_id):
        return [Show(show) for show in self.plex_api_call('sections/' + str(section_id) + '/all')]

    def get_seasons(self, show_id):
        return [Season(season) for season in self.plex_api_call('metadata/' + str(show_id) + '/children') if
                season.get('index') is not None]

    def get_season_episodes(self, season_id):
        return [Episode(episode) for episode in self.plex_api_call('metadata/' + str(season_id) + '/children', 'Video')]

    def get_show_episodes(self, show_id):
        return [Episode(episode) for episode in self.plex_api_call('metadata/' + str(show_id) + '/allLeaves', 'Video')]

    def get_video_files(self, episode_id):
        return [Video(video) for video in self.plex_api_call('metadata/' + str(episode_id), 'Part')]

    def plex_api_call(self, uri, m_type='Directory'):
        try:
            r = requests.get('http://' + self.__host__ + '/library/' + str(uri))
            rss = ET.fromstring(r.content)
            directories = rss.iter(m_type)
            ret = []
            for dir in directories:
                ret.append(dir.attrib)
            return ret

        except Exception as e:
            print e
            print "Plex API Error"
            return []


class PlexHelper():
    def __init__(self, plex_host=None):
        self.host = plex_host

    @staticmethod
    def get_se_array(show=None):
        if show is None:
            return []
        id = None
        if isinstance(show, Show):
            id = str(show.id)
        else:
            id = str(show)

        eps = ApiHelper().get_show_episodes(id)
        ret = []
        for episode in eps:
            ret.append(to_episode_string(episode.seasonNum, episode.episodeNum))

        return ret

    @staticmethod
    def generate_regex(show=None):
        if show is None:
            raise ValueError("Show needs to be defined")
        title = None
        if isinstance(show, Show):
            title = str(show.title)
        else:
            title = str(show)

        ret = title

        # Match the year case
        match = re.search('[(][0-9A-Za-z]{2,4}[)]$', ret)

        if match is not None and match.group() == ret[(-1 * len(match.group())):]:
            ret = ret[0:(-1 * len(match.group()))]

        # Remove white space
        ret = re.sub('[\W]', '.', ret)

        if ret[-1] == '.':
            ret += '*'
        else:
            ret += '.*'

        return ret

    @staticmethod
    def find_location(plex_id, episode_str):

        se = season_str_to_num(episode_str)

        if se is None:
            return None

        api = ApiHelper()

        seasons = api.get_seasons(plex_id)
        if seasons is None or len(seasons) == 0:
            return None

        found_season = None
        new_season = False

        for season in seasons:
            if season.seasonNum == se.get('season'):
                found_season = season

        if found_season is None:
            new_season = True
            found_season = seasons[-1]

        found_season.episodes = api.get_season_episodes(found_season.id)
        videos = api.get_video_files(found_season.episodes[0].id)
        if videos is None or len(videos) == 0:
            return None

        ret_value = path.dirname(videos[0].file)

        # new season needs a new directory
        if new_season is True:
            parent_path, season_path = path.split(ret_value)
            ret_value = path.join(parent_path, 'Season ' + str(se.get('season')))

        return ret_value

    @staticmethod
    def recursive_inflate(plex_object):

        if isinstance(plex_object, Show):
            for x in range(len(plex_object.get_seasons())):
                PlexHelper.recursive_inflate(plex_object.seasons[x])
            return plex_object
        elif isinstance(plex_object, Season):
            for x in range(len(plex_object.get_episodes())):
                PlexHelper.recursive_inflate(plex_object.episodes[x])
            return plex_object
        elif isinstance(plex_object, Episode):
            for x in range(len(plex_object.get_videos())):
                PlexHelper.recursive_inflate(plex_object.videos[x])
            return plex_object
        else:
            return plex_object


class Show():
    def __init__(self, kwargs):
        self.id = kwargs.get('ratingKey')
        self.title = kwargs.get('title')
        self.numEpisodes = int(kwargs.get('leafCount'))
        self.numSeasons = int(kwargs.get('childCount'))
        self.seasons = []

    def get_seasons(self):
        self.seasons = ApiHelper().get_seasons(self.id)
        return self.seasons


class Season():
    def __init__(self, kwargs):
        self.id = kwargs.get('ratingKey')
        self.numEpisodes = int(kwargs.get('leafCount'))
        self.seasonNum = int(kwargs.get('index'))
        self.episodes = []

    def get_episodes(self):
        self.episodes = ApiHelper().get_season_episodes(self.id)
        for eps in self.episodes:
            eps.seasonNum = self.seasonNum
        return self.episodes


class Episode():
    def __init__(self, kwargs):
        self.id = kwargs.get('ratingKey')
        self.episodeNum = kwargs.get('index')
        self.seasonNum = kwargs.get('parentIndex')
        self.videos = []

    def get_videos(self):
        self.videos = ApiHelper().get_video_files(self.id)
        return self.videos


class Video():
    def __init__(self, kwargs):
        self.file = kwargs.get('file')


def to_episode_string(season, episode):
    s = int(season)
    e = int(episode)
    ret = "S"
    if s > 9:
        ret += str(s)
    else:
        ret = ret + "0" + str(s)

    ret += "E"

    if e > 9:
        ret += str(e)
    else:
        ret = ret + "0" + str(e)

    return ret


def season_str_to_num(season_str):
    values = re.split('[SsEe]', season_str)

    if not (values is not None and len(values) > 2):
        return None  # This not expected

    return {
        "season": int(values[1]),
        "episode": int(values[2])
    }
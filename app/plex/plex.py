__author__ = 'Dirrk'

import xml.etree.ElementTree as ET

import requests
import app.settings as settings


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

    def get_all_shows(self, section_id):
        return self.plex_api_call('sections/' + str(section_id) + '/all')

    def get_seasons(self, show_id):
        seasons = self.plex_api_call('metadata/' + str(show_id) + '/children')
        return [season for season in seasons if season.get('index') is not None]


    def get_season_episodes(self, season_id):
        return self.plex_api_call('metadata/' + str(season_id) + '/children', 'Video')

    def get_show_episodes(self, show_id):
        return self.plex_api_call('metadata/' + str(show_id) + '/allLeaves', 'Video')

    def plex_api_call(self, uri, m_type='Directory'):
        try:
            r = requests.get('http://' + self.__host__ + '/library/' + str(uri))
            rss = ET.fromstring(r.content)
            directories = rss.findall(m_type)
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

    def get_se_array(self, show=None):
        if show is None:
            return []
        id = None
        if isinstance(show, Show):
            id = str(show.id)
        else:
            id = str(show)

        helper = ApiHelper(self.host)
        eps = helper.get_show_episodes(id)
        ret = []
        for episode in eps:
            ret.append(to_episode_string(episode.get('parentIndex'), episode.get('index')))

        return ret


class Show():
    def __init__(self, **kwargs):
        self.id = kwargs.get('ratingKey')
        self.title = kwargs.get('title')
        self.numEpisodes = int(kwargs.get('leafCount'))
        self.numSeasons = int(kwargs.get('childCount'))
        self.seasons = []


class Season():
    def __init__(self, **kwargs):
        self.id = kwargs.get('ratingKey')
        self.numEpisodes = int(kwargs.get('leafCount'))
        self.seasonNum = int(kwargs.get('index'))
        self.episodes = []


class Episode():
    def __init__(self, **kwargs):
        self.id = kwargs.get('ratingKey')
        self.episodeNum = kwargs.get('index')


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
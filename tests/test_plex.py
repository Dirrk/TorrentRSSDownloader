__author__ = 'Dirrk'

import unittest

from app.plex.plex import ApiHelper, PlexHelper, Show


class TestApiHelper(unittest.TestCase):
    def setUp(self):
        self.host = '192.168.137.1:32400'
        self.longMessage = True

    def test_PlexObject(self):
        a = ApiHelper(self.host)
        self.assertEqual(a.__host__, self.host)

    def test_plex_api(self):
        a = ApiHelper(self.host)
        data = a.plex_api_call('sections')
        self.assertEqual(len(data), 4)

    def test_plex_get_sections(self):
        a = ApiHelper(self.host)
        data = a.get_sections()
        print "Sections: ", data
        self.assertEqual(len(data), 4, "There should only be 4 sections on my plex server")

    def test_plex_get_shows(self):
        a = ApiHelper(self.host)
        data = a.get_all_shows('2')
        print "Shows: ", data
        self.assertGreater(len(data), 25, "There should be at least 25 shows under section 2 (TV Shows)")

    def test_plex_get_seasons(self):
        a = ApiHelper(self.host)
        data = a.get_seasons(713)
        print "Seasons: ", data
        self.assertEqual(len(data), 5, "There should be exactly 5 seasons of Breaking bad")

    def test_plex_get_episodes(self):
        a = ApiHelper(self.host)
        data = a.get_show_episodes(713)
        print "Episodes for show: ", data
        self.assertEqual(len(data), 62, "There should be exactly 62 episodes of Breaking bad")

    def test_plex_get_season_episodes(self):
        a = ApiHelper(self.host)
        data = a.get_season_episodes(714)
        print "Episodes for show: ", data
        self.assertEqual(len(data), 7, "Season 1 of breaking bad has 7 episodes")

    def test_plex_helper(self):
        a = PlexHelper(self.host)
        data = a.get_se_array(713)
        print "SE Array:", data
        self.assertEqual(len(data), 62, "There should be 62 episodes of Breaking Bad")

    def test_create_video(self):
        a = ApiHelper(self.host)
        video_files = a.get_video_files(765)
        self.assertEqual(len(video_files), 1, "S05E01 Should have 1 video")
        self.assertRegexpMatches(video_files[0].file, '.*S05E01.*')

    def test_create_show(self):
        val = {'rating': '8.4', 'art': '/library/metadata/4373/art/1391171227', 'addedAt': '1386945889', 'year': '2011',
               'ratingKey': '4373', 'viewedLeafCount': '0', 'studio': 'FX', 'key': '/library/metadata/4373/children',
               'updatedAt': '1391171227', 'duration': '3000000',
               'summary': 'American Horror Story is a horror-drama television franchise created and produced by Ryan Murphy and Brad Falchuk. Described as an anthology series, each season is conceived as a self-contained miniseries, following a disparate set of characters and settings, and a storyline with its own "beginning, middle and end".',
               'banner': '/library/metadata/4373/banner/1391171227', 'index': '1',
               'thumb': '/library/metadata/4373/thumb/1391171227', 'title': 'American Horror Story', 'leafCount': '38',
               'contentRating': 'TV-GA', 'originallyAvailableAt': '2011-10-05',
               'theme': '/library/metadata/4373/theme/1391171227', 'type': 'show', 'childCount': '3'}
        a = Show(val)
        self.assertEqual(a.id, '4373')

    def test_regex_1(self):
        a = PlexHelper()
        print a.generate_regex('Breaking Bad (2009)')
        self.assertEqual(a.generate_regex('Breaking Bad (2009)'), '^Breaking.Bad.*')
        self.assertEqual(a.generate_regex('Breaking Bad'), '^Breaking.Bad.*')
        self.assertEqual(a.generate_regex('Breaking Bad.'), '^Breaking.Bad.*')

    def test_regex_2(self):
        b = ApiHelper(self.host)
        a = PlexHelper(self.host)

        shows = b.get_all_shows(2)
        for show in shows:
            tmp_r = a.generate_regex(show.title)
            self.assertRegexpMatches(show.title, tmp_r)

    def test_dir_finder(self):
        a = PlexHelper(self.host)
        loc = a.find_location(713, 'S05E17')
        print "Location:", loc
        self.assertEqual("Y:\\TV\\Breaking Bad\\Season 5", loc)

    def test_dir_finder_new_dir(self):
        a = PlexHelper(self.host)
        loc = a.find_location(713, 'S06E01')
        print "Location:", loc
        self.assertEqual("Y:\\TV\\Breaking Bad\\Season 6", loc)

    def test_inflate(self):
        a = ApiHelper(self.host).get_show_by_id(713)
        self.assertIsInstance(a, Show)
        a = PlexHelper.recursive_inflate(a)
        self.assertEqual(a.numSeasons, len(a.seasons))
        self.assertEqual(a.seasons[0].numEpisodes, 7)
        self.assertEqual(a.seasons[-1].numEpisodes, 16)
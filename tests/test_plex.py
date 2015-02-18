__author__ = 'Dirrk'

import unittest

from app.plex.plex import ApiHelper, PlexHelper


class TestApiHelper(unittest.TestCase):
    def setUp(self):
        self.host = '192.168.137.1:32400'

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

    def test_regex_1(self):
        a = PlexHelper()
        print a.generate_regex('Breaking Bad (2009)')
        self.assertEqual(a.generate_regex('Breaking Bad (2009)'), 'Breaking.Bad.*')
        self.assertEqual(a.generate_regex('Breaking Bad'), 'Breaking.Bad.*')
        self.assertEqual(a.generate_regex('Breaking Bad.'), 'Breaking.Bad.*')

    def test_regex_2(self):
        b = ApiHelper(self.host)
        a = PlexHelper(self.host)

        shows = b.get_all_shows(2)
        for show in shows:
            tmp_r = a.generate_regex(show.get('title'))
            print "Regex for show:", show.get('title'), "is", tmp_r
            self.assertRegexpMatches(show.get('title'), tmp_r)

__author__ = 'Dirrk'

import unittest

import app.torrent.bencode as bencode
import os
from app.torrent.Torrent import Torrent, TORRENT_STATES, extract_file



class TestBEncode(unittest.TestCase):
    def setUp(self):
        self.files = []
        for (dirpath, dirnames, filenames) in os.walk("F:\\test-area\\bencode\\"):
            for file in filenames:
                self.files.append(dirpath + file)
            break
        for f in self.files:
            print f

    def test_b_encode(self):

        for f in self.files:

            info = bencode.torrent_file_to_dictionary(f)
            self.assertIsInstance(info, dict)
            self.assertIsInstance(info['name'], str)
            print "Folder name found: ", info['name']
            if info.get('files') is None:
                self.assertRegexpMatches(info.get('name'), '[\.][a-zA-Z]{3}$')
            else:
                self.assertGreater(len(info.get('files')), 0)


                # data = '8:announce72:http://sync.empirehost.me:9153/TOKEN/announce4:infod5:filesld6:lengthi1217626673e4:pathl41:Big Hero 6 2014 DVDSCR x264 AC3 TiTAN.mkveed6:lengthi3086e4:pathl41:Big Hero 6 2014 DVDSCR x264 AC3 TiTAN.nfoeee4:name37:Big Hero 6 2014 DVDSCR x264 AC3 TiTAN12:piece lengthi2097152'
                # values = bencodeToDict(data)


class TestTorrent(unittest.TestCase):
    def setUp(self):
        self.a = Torrent(
            "https://iptorrents.com/download.php/1323172/Treehouse.Masters.S03E05.Lost.in.the.Forest.720p.HDTV.x264-DHD.torrent?torrent_pass=TOKEN")

    def test_torrent_file(self):
        self.assertEqual(self.a.file,
                         "F:\\test-area\\dev\\monitor\\Treehouse.Masters.S03E05.Lost.in.the.Forest.720p.HDTV.x264-DHD.torrent")

    def test_download_file(self):
        self.assertTrue(self.a.download())
        self.assertEqual(self.a.folder, "Treehouse.Masters.S03E05.Lost.in.the.Forest.720p.HDTV.x264-DHD")
        self.assertTrue(os.path.exists(self.a.file))

    def test_check_status(self):
        self.assertEqual(self.a.status, TORRENT_STATES["NEW"])
        self.assertFalse(self.a.check_status())
        self.assertEqual(self.a.status, TORRENT_STATES["TORRENT_RETRIEVED"])

    def test_organize(self):
        self.assertEqual(1, 0)

    def test_extract(self):
        self.assertTrue(extract_file(
            "F:\\test-area\\dev\\complete\\My.Favorite.Show.S01E02\\Laggies.2014.LIMITED.720p.BRRiP.X264.Ac3.CrEwSaDe.Sample.zip.001",
            "F:\\test-area\\dev\\Plex_Area\\Drive A\\TV\\Show ABC\\S1"))
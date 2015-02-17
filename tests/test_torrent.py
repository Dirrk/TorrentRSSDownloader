__author__ = 'Dirrk'

import unittest

import app.torrent.bencode as bencode
import os
from app.torrent.Torrent import Torrent


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
    def test_torrentCreate(self):
        a = Torrent(
            "https://iptorrents.com/download.php/1323172/Treehouse.Masters.S03E05.Lost.in.the.Forest.720p.HDTV.x264-DHD.torrent?torrent_pass=TOKEN")
        self.assertEqual(a.file,
                         "F:\\torrent_files\\Treehouse.Masters.S03E05.Lost.in.the.Forest.720p.HDTV.x264-DHD.torrent")
        self.assertTrue(a.download())
        self.assertEqual(a.folder, "Treehouse.Masters.S03E05.Lost.in.the.Forest.720p.HDTV.x264-DHD")
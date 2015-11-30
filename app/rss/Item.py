__author__ = 'Dirrk'
from datetime import datetime as date
import xml.etree.ElementTree as ET
import logging

import re

es = re.compile("(20[0-9][0-9].[0-9]+.[0-9]+|S[0-9]+(?:E[0-9][0-9])+)", re.IGNORECASE)


class Item:
    def __init__(self, xml_element):
        """
        RSS Item
        :param xml_element: xml.etree.ElementTree.Element
        """
        if not isinstance(xml_element, ET.Element):

            if not isinstance(xml_element, basestring):
                raise TypeError(
                    "Invalid usage Item(xml_element) requires argument type xml.etree.ElementTree.Element or xml string")
                return

            try:
                xml_element = ET.fromstring(xml_element)
            except:
                raise TypeError(
                    "Invalid usage Item(xml_element) requires argument type xml.etree.ElementTree.Element or xml string")
                return

        try:
            self.title = xml_element.find('title').text
            self.pubDate = date.strptime(xml_element.find('pubDate').text, "%a, %d %b %Y %H:%M:%S +0000")
            self.description = xml_element.find('description').text
            self.link = xml_element.find('link').text
        except Exception as e:
            logging.exception(e)

        self.size = parse_size(self.description)
        self.episodes = parse_episode(self.title)
        self.quality = parse_quality(self.title)


def parse_size(desc):
    size = -1
    size_strings = re.split(' ', re.split(';', desc)[0])
    if len(size_strings) >= 2:
        size = int(float(size_strings[0]))
        if size_strings[1].upper() == "GB":
            size *= 1000
        elif size_strings[1].upper() == "TB":
            size *= 1000000
    return int(size)


def parse_episode(title):
    episode = ""
    ret = []
    ep = es.search(title)
    if ep is not None:
        episode = ep.group().replace(" ", "").replace("-", "").replace(".", "")
        data = re.split('[E]', episode, re.IGNORECASE)
        season = data[0]
        if len(data) > 1:
            episodes = data[1:]
            for ep in episodes:
                ret.append(season + "E" + ep)
        else:
            ret.append(season)
    else:
        return [""]

    return ret


def parse_quality(title):
    quality = -1
    q = re.search('(4096|1080|720|480)', title)
    if q is not None:
        quality = int(q.group())

    q = re.search('(264|HDTV|BluRay|BD|4K)', title)
    if q is not None:
        quality += len(q.groups())

    return quality
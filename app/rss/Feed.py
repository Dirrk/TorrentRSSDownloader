__author__ = 'Dirrk'
import xml.etree.ElementTree as ET
import time

import requests
from app.rss.Item import Item


class Feed:
    def __init__(self, id, url, name="new feed", frequency=300):
        """
        Create Feed
        :param id: id
        :param url: url to download feed items
        :param name: name of feed
        :param frequency: time in seconds to wait
        """
        self.name = name
        self.url = url
        self.id = id
        self.frequency = frequency
        self.last_run = 0
        self.last_pub = 0

    def fetch_items(self):
        """
        Fetch RSS Feed
            Ignore items older than last_run
            create new item objects for new items in rss feed
        :return: Array of Items
        """
        items = []

        try:
            # Download from url
            r = requests.get(self.url)

            # Parse rss data
            rss = ET.fromstring(r.content)

            rss_items = rss.findall('*/item')

            # Create Item Objects
            for rss_item in rss_items:

                try:
                    temporary_item = Item(rss_item)

                    # If newer than last pub add to return items
                    if time.mktime(temporary_item.pubDate.timetuple()) > self.last_pub:
                        items.append(temporary_item)
                except ValueError:
                    print "Could not process an rss_item skipping"
        except ValueError:
            print "Unable to retrieve rss data or failed parsing data"

        self.last_run = time.time()
        return items

    def update_cycle(self):
        """
        Update Cycle
        :return: True/False if enough time has elapsed since last lookup
        """
        if time.time() - self.last_run >= self.frequency:
            return True
        else:
            return False
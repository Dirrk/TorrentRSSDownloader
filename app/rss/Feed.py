__author__ = 'Dirrk'
import xml.etree.ElementTree as ET
import time
import logging

import requests
from app.rss.Item import Item


logging.getLogger("requests").setLevel(logging.WARNING)

# id, url, name, frequency


class Feed:
    def __init__(self, id, url, name="new feed", frequency=300, last_pub=0):
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
        self.last_run = last_pub

    def fetch_items(self):
        """
        Fetch RSS Feed
            Ignore items older than last_run
            create new item objects for new items in rss feed
        :return: Array of Items
        """
        items = []

        logging.info("Feed " + self.name + " is retrieving list")

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
                    items.append(temporary_item)
                except ValueError:
                    logging.error("Could not process an rss_item skipping")
        except ValueError as e:
            logging.error("Unable to retrieve rss data or failed parsing data")
            logging.exception(e)
        except ET.ParseError as e:
            logging.error("ParseError with feed " + e.message)
            logging.exception(e)

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
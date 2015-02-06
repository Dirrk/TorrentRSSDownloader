__author__ = 'Dirrk'
import datetime
import time

import re


"""
 Subscription.py
 Subscription Object
    Name
    Regex include string
    Regex exclude string
    EpisodeMatch = true/false
    Episodes: [
        "S01E01",
        "S01E02",
        "S01E03",
        "S01E04",
        ]
    }
"""


class Subscription:
    def __init__(self, id, name, feed_id, inopts={}):
        """
        Subscription Object
        :param name:
        :param reg_allow:
        :param reg_exclude:
        """
        self.id = id
        self.name = name
        self.feedId = feed_id
        self.episodes = []
        options = {}

        options['reg_allow'] = inopts.get('reg_allow') if inopts.get('reg_allow') is not None else ""
        options['reg_exclude'] = inopts.get('reg_exclude') if inopts.get(
            'reg_exclude') is not None else "555DO-NOT-MATCH-THIS-REGEX-ESCAPE555"
        options['enabled'] = inopts.get('enabled') if inopts.get('enabled') is not None else False
        options['waitTime'] = inopts.get('waitTime') if inopts.get('waitTime') is not None else 0  # Hours
        options['lastMatched'] = inopts.get('lastMatched') if inopts.get('lastMatched') is not None else 0
        options['minSize'] = inopts.get('minSize') if inopts.get('minSize') is not None else 0
        options['maxSize'] = inopts.get('maxSize') if inopts.get(
            'maxSize') is not None else 1000000000  # Max of one petabyte ;)
        options['quality'] = inopts.get('quality') if inopts.get('quality') is not None else -1
        options['episode_match'] = inopts.get('episode_match') if inopts.get('episode_match') is not None else False
        options['onlyOnce'] = inopts.get('onlyOnce') if inopts.get('onlyOnce') is not None else False
        options['preferred_release'] = inopts.get('preferred_release') if inopts.get(
            'preferred_release') is not None else ""

        self.__options__ = options

    def add_episode(self, id):
        try:
            self.episodes.index(id)
            print "Cannot add an episode that is already found"
        except ValueError:
            self.episodes.append(id)
        finally:
            return len(self.episodes)

    def set_option(self, key, value):
        self.__options__[key] = value

    def match(self, items):

        print "Matching"
        if self.__options__.get('enabled') is not True:
            print "Not enabled"
            return []
        if self.__options__.get('waitTime') != 0 and (datetime.datetime.now() - time.localtime(
                self.__options__.get('lastMatched'))).seconds < self.__options__.get('waitTime') * 3600:
            print "WaitTime: ", self.__options__.get("waitTime")
            return []

        matches = []
        allow = re.compile(self.__options__.get('reg_allow'), re.IGNORECASE)
        exclude = re.compile(self.__options__.get('reg_exclude'), re.IGNORECASE)
        pref_release = re.compile(self.__options__.get('preferred_release'), re.IGNORECASE)

        # First round of matching via title
        for item in items:
            test_allow = allow.search(item.title)
            if test_allow is not None:
                test_exclude = exclude.search(item.title)
                if test_exclude is None:
                    matches.append(item)
                    print "Round #1 match: ", item.title

        matches2 = {
            "__NO__EPISODE__": []
        }


        # Second round of matching
        for match in matches:
            # Size / Quality
            if (match.size == -1 or (match.size > self.__options__.get('minSize') and match.size < self.__options__.get(
                    'maxSize'))) and (match.quality == -1 or match.quality >= self.__options__.get('quality')):

                # Find release info
                p = pref_release.search(match.title)
                if p is not None:
                    match.quality += len(p.groups()) * 10

                print "Round #2 (After Size/Quality): ", item.title

                # Filter episodes
                if self.__options__.get('episode_match') is True and len(match.episode) > 2:
                    try:
                        self.episodes.index(match.episode)
                    except ValueError:
                        if matches2.get(match.episode) is None:
                            matches2[match.episode] = [match]
                        else:
                            matches2[match.episode].append(match)
                else:
                    matches2["__NO__EPISODE__"].append(match)

        return_matches = []
        for key in matches2.keys():
            if len(matches2[key]) > 0:
                # Sort for best quality
                matches2[key].sort(lambda a, b: a.quality - b.quality)

                # Add to return stack
                return_matches.append(matches2[key][0])
                print "Final round: ", matches2[key][0].title
                self.__options__["lastMatched"] = time.time()

                # Add to episode list
                if key != "__NO__EPISODE__":
                    self.episodes.append(key)

        if len(return_matches) > 0 and self.__options__.get('onlyOnce') is True:
            self.__options__["enabled"] = False

        return return_matches
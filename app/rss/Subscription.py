__author__ = 'Dirrk'
import time
import logging

import re


class Subscription:
    def __init__(self, id, name, feedid, plex_id=0, enabled=1, reg_allow='', match_type='episode',
                 preferred_release='', max_size=1000000000, min_size=0,
                 reg_exclude="555DO-NOT-MATCH-THIS-REGEX-ESCAPE555", quality=-1, last_matched=0):
        """
        Subscription Object
        :param name:
        :param reg_allow:
        :param reg_exclude:
        """
        self.id = id
        self.name = name
        self.feedId = feedid
        self.episodes = []
        self.plex_id = plex_id
        self.enabled = enabled
        self.reg_allow = reg_allow
        self.match_type = match_type
        self.preferred_release = preferred_release
        self.max_size = max_size
        self.min_size = min_size
        self.reg_exclude = reg_exclude
        self.quality = quality
        self.last_matched = last_matched

    def add_episode(self, id):
        try:
            self.episodes.index(id)
        except ValueError:
            self.episodes.append(id)
        finally:
            return len(self.episodes)

    def match(self, items):

        matches = []
        allow = re.compile(self.reg_allow, re.IGNORECASE)
        exclude = re.compile(self.reg_exclude, re.IGNORECASE)
        pref_release = re.compile(self.preferred_release, re.IGNORECASE)

        # First round of matching via title
        for item in items:
            test_allow = allow.search(item.title)
            if test_allow is not None:
                if self.reg_exclude == "555DO-NOT-MATCH-THIS-REGEX-ESCAPE555" or self.reg_exclude == '':
                    matches.append(item)
                else:
                    test_exclude = exclude.search(item.title)
                    if test_exclude is None:
                        matches.append(item)

        matches2 = {
            "__NO__EPISODE__": []
        }

        # Second round of matching
        for match in matches:
            # Size / Quality
            if not (not (match.size == -1 or (match.size > self.min_size and match.size < self.max_size)) or not (
                            match.quality == -1 or match.quality >= self.quality)):

                # Find release info
                p = pref_release.search(match.title)
                if p is not None:
                    match.quality += len(p.groups()) * 10

                # Filter episodes
                if self.match_type == 'episode' and len(match.episodes) >= 1:
                    for ep in match.episodes:
                        try:
                            if len(ep) > 3:
                                self.episodes.index(ep)
                                logging.debug("Match blocked, because episode already exists " + str(ep))
                        except ValueError:
                            if matches2.get(ep) is None:
                                matches2[ep] = [match]
                            else:
                                matches2[ep].append(match)
                elif self.match_type == 'once':
                    logging.warn("Match type was not implemented!")
                else:
                    matches2["__NO__EPISODE__"].append(match)

        return_matches = []

        for key in matches2.keys():
            if len(matches2[key]) > 0:
                # Sort for best quality
                matches2[key].sort(lambda a, b: b.quality - a.quality)

                # Add to return stack
                return_matches.append(matches2[key][0])
                logging.debug("Final round: " + str(matches2[key][0].title))
                self.last_matched = time.time()

                # Add to episode list
                if key != "__NO__EPISODE__":
                    self.episodes.append(key)

        if len(return_matches) > 0 and self.match_type == 'onlyOnce':
            self.enabled = 0

        return return_matches
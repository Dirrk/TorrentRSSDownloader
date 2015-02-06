'''
    https://wiki.theory.org/Decoding_bencoded_data_with_python
    This was taken from the above site which was referenced on the bittorrent site
'''
__author__ = 'Hackeron'

import logging

import re


decimal_match = re.compile('\d')


def bdecode(data):
    '''Main function to decode bencoded data'''
    print "Decoding data: ", data
    chunks = list(data)
    chunks.reverse()
    root = _dechunk(chunks)
    return root


def _dechunk(chunks):
    item = chunks.pop()

    if item == 'd':
        item = chunks.pop()

        hash = {}
        while item != 'e':
            chunks.append(item)
            key = _dechunk(chunks)
            hash[key] = _dechunk(chunks)
            item = chunks.pop()
        return hash
    elif item == 'l':
        item = chunks.pop()

        list = []
        while item != 'e':
            chunks.append(item)
            list.append(_dechunk(chunks))
            item = chunks.pop()
        return list
    elif item == 'i':

        item = chunks.pop()
        num = ''
        while item != 'e':
            num += item
            item = chunks.pop()
        return int(num)
    elif decimal_match.search(item):
        num = ''
        while decimal_match.search(item):
            num += item
            item = chunks.pop()
        line = ''
        for i in range(int(num)):
            line += chunks.pop()
        return line
    raise "Invalid input!"


def torrent_file_to_dictionary(a_file):
    """
    Read in torrent file
    :param a_file: Torrent File
    :return: Dictionary of info object
    """
    ret_dict = {}

    # Open File
    with open(a_file, mode='r') as f:

        torrent_info = f.readline()

        # Regex the part I want
        match = re.match('d.*e6.pieces', torrent_info)
        torrent_line = match.group()[:-8]

        # Cut off bencode with ee to stop any list / dict
        try:
            test_data = bdecode(torrent_line + 'eee')
            ret_dict = test_data['info']

        except Exception as e:
            logging.exception(e)

    return ret_dict
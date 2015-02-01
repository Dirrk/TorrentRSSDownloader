__author__ = 'Dirrk'

import json
import logging

import os.path as path

log = logging.getLogger()


def reader(a_file):
    # read a_file
    if path.isfile(a_file):
        log.info("json file found attempting to parse")
        try:
            # Open file in read only mode using with here skips the need to close it
            with open(a_file, mode='r') as f:
                return json.load(f)

        except (IOError, ValueError) as e:

            if isinstance(e, IOError):
                log.error("Error reading json file: %s" % a_file)
            else:
                log.error("Error parsing json file: %s please check json format" % a_file)
            raise e


def writer(a_file, str_data):
    if path.isfile(a_file):
        log.info("json file found attempting to stringify")
        try:
            # Open file in read only mode using with here skips the need to close it
            with open(a_file, mode='w') as f:
                return json.dump(f, str_data)

        except (IOError, ValueError) as e:

            if isinstance(e, IOError):
                log.error("Error reading json file: %s" % a_file)
            else:
                log.error("Error parsing json file: %s please check json format" % a_file)
            raise e

__author__ = 'Dirrk'

__myConfig__ = None


class Config:
    def __init__(self, arg):
        self.__store__ = {}
        for key in arg.keys():
            self.__store__[key] = arg[key]

    def set(self, key, value):
        self.__store__[key] = value

    def get(self, key):
        return self.__store__[key]


def conf(arg=None):
    if arg is None:
        return __myConfig__
    else:
        return Config(arg)
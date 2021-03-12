import os
import time
import json
#from werkzeug.routing import BaseConverter
 

ROOT_DIR = 'test'
STATIC_DIR = 'static'

"""class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]"""

class File(object):
    def __init__(self, path, fileName):
        fullPath = os.path.join(path, fileName)
        statinfo = os.stat(fullPath)
        self.name = fileName
        self.path = fullPath.replace('\\', '/').replace(ROOT_DIR + '/', '', 1)
        if os.path.isdir(fullPath):
            self.type = 0
        elif os.path.isfile(path):
            self.type = 1
        else:
            self.type = 2
        self.size = statinfo.st_size
        self.mtime = time.strftime("%Y-%m-%d %H:%M:%S",
                                   time.localtime(statinfo.st_mtime))


def listFile(path: str) -> []:
    return [File(path, fileName) for fileName in os.listdir(path)]

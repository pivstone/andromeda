import sys

__author__ = 'pivstone'

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
PY34 = sys.version_info[0:2] >= (3, 4)

if PY2:
    def convert2timestamp(datetime):
        import time
        return int(time.mktime(datetime.timetuple()) * 1e3 + datetime.microsecond / 1e3)

if PY3:
    def convert2timestamp(datetime):
        return datetime.timestamp() * 1000

import sys
import threading
import logging

logger = logging.getLogger(__name__)

class ProgressBytes(object):
    def __init__(self, filename):
        self._filename = filename
        self._seen_so_far = 0
        self._lock = threading.Lock()
    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            logging.info(
                "%s --> %s bytes transferred" % (
                    self._filename, self._seen_so_far))
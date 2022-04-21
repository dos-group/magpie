import time
from pathlib import Path

# app root path
APP_ROOT = str(Path(__file__).parent.parent)


def time_start():
    return time.time()


def time_end(start):
    end = time.time()
    delay = end - start
    return delay

import time


def current_milli_time():
    return int(round(time.time() * 1000))


def current_nano_time():
    return int(round(time.time() * 1000000))

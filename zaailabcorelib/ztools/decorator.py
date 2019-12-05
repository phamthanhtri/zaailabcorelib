# -----------------------------------------------------------
# decorator.py
#
# (C) 2019 HCMC, Vietnam
# Released under GNU Public License (GPL)
# email congvm.it@gmail.com
# -----------------------------------------------------------

import traceback
from time import time


def zlogging_deco(default_value, logger=None):
    """ Logging Decorator
        Automatically logging with exception handler.
        Parameters
        -----------
        default_value: type of default value
            Return default_value if exception
        
        logger: custom logging, optional
            Logging with logger instead of printing log out
    """
    log_id = str(time())

    def print_log(msg, log_level):
        if logger is not None:
            assert log_level in ['info', 'exception', 'error', 'debug']
            if log_level == 'info':
                logger.info(msg)
            elif log_level == 'exception':
                logger.exception(msg)
            elif log_level == 'error':
                logger.exception(msg)
            elif log_level == 'debug':
                logger.debug(msg)
        else:
            print(msg)

    def nested(func):
        def wrapper(*args, **kwargs):
            print_log("[{}][Input] - {} - {} - log_id: {}".format(
                func.__name__.upper(), args, kwargs, log_id), log_level='info')
            try:
                result = func(*args, **kwargs)
                print_log("[{}][Result] - {} - log_id: {}".format(
                    func.__name__.upper(), result, log_id), log_level='info')
                if type(result) != type(default_value):
                    print_log("[{}][Result][WARNING] - {} - log_id: {}".format(
                        func.__name__.upper(), result, log_id), log_level='info')
                return result
            except:
                print_log("[{}][Result] - {} - log_id: {}".format(func.__name__.upper(),
                                                                  traceback.format_exc(), log_id), log_level='exception')
                return default_value
        return wrapper
    return nested

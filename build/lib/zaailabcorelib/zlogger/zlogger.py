import configparser
import logging.config
import os
from logging.handlers import TimedRotatingFileHandler

from zaailabcorelib.zlogger.constant import DEV_FILENAME, PROD_FILENAME, STAG_FILENAME


class Zlogger():
    __instance = None

    @staticmethod
    def get_logger():
        if Zlogger.__instance is None:
            Zlogger.__instance = Zlogger()
        return Zlogger.__instance

    def __init__(self, config_dir='./conf'):
        self._config_dir = config_dir
        self._getConfigDirectory()
        try:
            env = os.environ['SERVICE_ENV_SETTING']
            assert env in ["DEVELOPMENT", "PRODUCTION", "STAGING"]
        except:
            raise ValueError(
                "The environment param `SERVICE_ENV_SETTING` need to be assigned as: DEVELOPMENT | PRODUCTION | STAGING")

        if env == 'DEVELOPMENT':
            self.conf = self._development()
        elif env == 'STAGING':
            self.conf = self._staging()
        elif env == 'PRODUCTION':
            self.conf = self._production()
        cfg_path = None
        if self.conf.has_section('logger'):
            cfg_path = self.conf['logger']

        if cfg_path is not None and self.conf.get('logger', 'log_dir') is not None:
            log_dir = self.conf['logger'].get('log_dir', '/data/log/' + os.environ['NAME'])
        else:
            log_dir = '/data/log/' + os.environ['NAME']

        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        logging.config.fileConfig(self._config_dir + '/logging.conf')
        info_logger_handler = TimedRotatingFileHandler(
            filename=log_dir + '/info_' + os.environ['NAME'] + '.log', when='midnight', interval=1,
            backupCount=10)
        self.info_logger = logging.getLogger('MainLogger_info')
        self.info_logger.propagate = False

        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(filename)s-%(funcName)s-%(lineno)04d | %(message)s')
        info_logger_handler.setFormatter(formatter)
        self.info_logger.addHandler(info_logger_handler)

        error_logger_handler = TimedRotatingFileHandler(
            filename=log_dir + '/error_' + os.environ['NAME'] + '.log', when='midnight', interval=1,
            backupCount=10)
        self.error_logger = logging.getLogger('MainLogger_error')
        self.error_logger.propagate = False

        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(filename)s-%(funcName)s-%(lineno)04d | %(message)s')
        error_logger_handler.setFormatter(formatter)
        self.error_logger.addHandler(error_logger_handler)

    def _development(self):
        configParser = configparser.ConfigParser()
        configParser.read(self._dev_config_paths)
        return configParser

    def _staging(self):
        configParser = configparser.ConfigParser()
        configParser.read(self._stag_config_paths)
        return configParser

    def _production(self):
        configParser = configparser.ConfigParser()
        configParser.read(self._prod_config_paths)
        return configParser

    def _getConfigDirectory(self):
        self._dev_config_paths = os.path.join(self._config_dir, DEV_FILENAME)
        self._prod_config_paths = os.path.join(self._config_dir, PROD_FILENAME)
        self._stag_config_paths = os.path.join(self._config_dir, STAG_FILENAME)
        for f in [self._dev_config_paths, self._prod_config_paths, self._stag_config_paths]:
            if not os.path.exists(f):
                raise FileNotFoundError("File not found: {}".format(f))

    def info(self, msg):
        self.info_logger.info(msg)

    def error(self, msg):
        self.error_logger.error(msg)

    def exception(self, msg):
        self.error_logger.exception(msg)

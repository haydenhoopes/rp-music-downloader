import logging
import os
import re
from datetime import datetime, timedelta


# custom log levels
SUCCESS_LEVEL_NUM = 25
FAILED_LEVEL_NUM = 45

logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")
logging.addLevelName(FAILED_LEVEL_NUM, "FAILED")


def success(self, message, *args, **kws):
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        self._log(SUCCESS_LEVEL_NUM, message, args, **kws)


def failed(self, message, *args, **kws):
    if self.isEnabledFor(FAILED_LEVEL_NUM):
        self._log(FAILED_LEVEL_NUM, message, args, **kws)


# Attach custom methods to logger
logging.Logger.success = success
logging.Logger.failed = failed


class Logger:
    def __init__(self, name, log_level='info'):
        self.today = datetime.now()
        self.logs_dir = self.__find_logs_dir()
        self.log_file = f'{self.logs_dir}/{name}_{self.today.strftime("%Y-%m-%d")}.log'

        self.logger = logging.getLogger(name)
        self.__purge_old_logs()
        self.__create_logger(log_level)


    def __create_logger(self, log_level):
        self.logger.setLevel(self.__get_log_level(log_level))
        self.logger.propagate = False

        if not self.logger.handlers:
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.__get_log_level(log_level))
            console_handler.setFormatter(ColoredFormatter(
                fmt="%(asctime)-24s %(levelname)-20s %(filename)-26s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            ))

            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(self.__get_log_level(log_level))
            file_handler.setFormatter(logging.Formatter(
                fmt="%(asctime)-24s %(levelname)-20s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            ))

            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)


    def __get_log_level(self, level):
        return {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'success': SUCCESS_LEVEL_NUM,
            'failed': FAILED_LEVEL_NUM,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }.get(level.lower(), logging.INFO)


    def __find_logs_dir(self):
        for path in ['logs', '../logs', '../../logs']:
            if os.path.isdir(path):
                return path
        os.makedirs('logs', exist_ok=True)
        return 'logs'


    def __purge_old_logs(self):
        cutoff_date = self.today - timedelta(days=400)
        pattern = re.compile(r"\w+_(\d{4})-(\d{2})-(\d{2})\.log")

        for filename in os.listdir(self.logs_dir):
            match = pattern.match(filename)
            if match:
                year, month, day = map(int, match.groups())
                file_date = datetime(year, month, day)

                if file_date < cutoff_date:
                    file_path = os.path.join(self.logs_dir, filename)
                    os.remove(file_path)


    def get_logger(self):
        return self.logger


class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[34m',     # Blue
        'INFO': '\033[37m',      # White
        'WARNING': '\033[33m',   # Yellow
        'SUCCESS': '\033[32m',   # Green
        'FAILED': '\033[31m',    # Red
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[31m'   # Red
    }
    RESET = '\033[0m'


    def format(self, record):
        color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)



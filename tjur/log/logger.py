import logging
import os
import sys
import time

from datetime import date


class Logger():

    def __init__(self, config):
        self.config = config
        filename = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), 'tjur.log')
        logging.basicConfig(
            filename=filename,
            format='%(asctime)s.%(msecs)06d %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            level=self.config['log']['level'] or 'INFO')
        logging.Formatter.converter = time.gmtime

    def debug(self, msg):
        logging.debug(msg)

    def info(self, msg):
        logging.info(msg)

    def warn(self, msg):
        logging.warning(msg)

    def error(self, msg):
        logging.error(msg)

    def log_print_and_exit(self, msg):
        logging.info(msg)
        print(msg)
        sys.exit(0)

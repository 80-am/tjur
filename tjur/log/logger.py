import logging
import os
import sys
import time


class Logger():

    filename = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'tjur.log')
    logging.basicConfig(
        filename=filename,
        format='%(asctime)s.%(msecs)06d %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO)
    logging.Formatter.converter = time.gmtime

    def log(self, msg):
        logging.info(msg)

    def log_print(self, msg):
        logging.info(msg)
        print(msg)

    def log_print_and_exit(self, msg):
        logging.info(msg)
        print(msg)
        sys.exit(0)

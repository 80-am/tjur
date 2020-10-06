import logging
import os
import sys
import time

from datetime import datetime


class Logger():

    tjur_dir = os.path.dirname(sys.argv[0])
    logging.basicConfig(
        filename=tjur_dir + '/log/tjur-' + str(
            datetime.timestamp(
                datetime.utcnow())) + '.log',
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

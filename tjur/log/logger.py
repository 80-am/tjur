import curses
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
        if self.config['ui']:
            self.stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
        else:
            path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(path, '../assets/start-up.txt')) as f:
                print(f.read())

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

    def write_to_screen(self, y, x, msg):
        if self.config['ui']:
            self.stdscr.clrtoeol()
            self.stdscr.addstr(y, x, msg)
            self.stdscr.refresh()

    def clear_lines(self, from_y, to_y):
        if self.config['ui']:
            for i in range(from_y, to_y):
                self.stdscr.clrtoeol()
                self.stdscr.addstr(i, 0, '')
                self.stdscr.refresh()

import pkg_resources
import sys
from argparse import ArgumentParser


class Parser(object):

    def __init__(self):
        self._parser = ArgumentParser(prog='tjur', add_help=False)
        self._add_arguments()

    def _add_arguments(self):
        self._parser.add_argument(
            '-t', '--trade',
            action='store_true',
            help='start tjur in trade mode')
        self._parser.add_argument(
            '-v', '--version',
            action='store_true',
            help=self.get_version())
        self._parser.add_argument(
            '-h', '--help',
            action='store_true',
            help='show this help message and exit')

    def parse(self):
        return self._parser.parse_args()

    def print_usage(self):
        self._parser.print_usage(sys.stderr)

    def print_help(self):
        self._parser.print_help(sys.stderr)

    def get_version(self):
        return 'tjur ' + str(pkg_resources.require('tjur')[0].version)

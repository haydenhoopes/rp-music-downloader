import argparse
from pathlib import Path
import sys


class Commandline:
    def __init__(self, logger):
        self.logger = logger
        self.args = self.__set_arguments()


    def __set_arguments(self):
        self.parser = argparse.ArgumentParser(description='A command line interface for downloading music from YouTube')

        self.parser.add_argument('--skip-api', action='store_true', help='Flag indicating to skip checking for new songs added to playlists (only download previously discovered songs).')
        self.parser.add_argument('--skip-download', action='store_true', help='Flag indicating to skip downloading to USB (only update database).')
        self.parser.add_argument('--reset', action='store_true', help='Flag indicating to drop all tables and start over')
        self.parser.add_argument('-p', '--playlist-ids', required=False, metavar='', help='Comma separated list of playlist ids.')

        self.args = self.parser.parse_args()

        if not self.args.skip_api and not self.args.playlist_ids:
            self.logger.warning('no playlist ids provided, will use all previously identified playlists')
        if self.args.skip_api and self.args.skip_download:
            raise Exception('cannot skip api and download at the same time')
        if self.args.skip_api:
            self.logger.info('skipping check for new playlist items')
        if self.args.skip_download:
            self.logger.info('skipping download')

        return self.args


    def execute(self):
        return self.args

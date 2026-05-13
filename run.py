#!/usr/bin/env python


import sys

from modules.usb import USB
from modules.db import Database
from modules.ddl import DDL
from modules.api import API
from modules.downloader import Downloader
from modules.logger import Logger
from modules.commandline import Commandline


class MusicDownloader:
    def __init__(self):
        self.logger = Logger('rp-music-download').logger
        commandline = Commandline(self.logger)
        self.args = commandline.execute()

        self.db = Database(self.logger)
        self.db.connect()

        self.ddl = DDL(self.logger, self.db)
        self.ddl.execute(self.args)

        self.api = API(self.logger, self.db)
        self.usb = USB(self.logger, self.db)
        self.downloader = Downloader(self.logger, self.db)


    def get_stored_playlist_ids(self):
        sql = f"""
            SELECT
                playlist_id
            FROM
                Playlists
            ;
        """
        results = self.db.execute(sql)

        self.logger.info(f'found {len(results)} previously identified playlists:')

        return ','.join([row[0] for row in results])


    def merge_playlists(self, playlists):
        self.logger.info('updating `Playlist` table')

        for playlist in playlists:
            sql = f"""
                INSERT OR IGNORE INTO Playlists (
                    playlist_id, playlist_name
                ) VALUES (?, ?);
            """
            self.db.execute(sql, [playlist['id'], playlist['snippet']['title']])


    def merge_songs(self, playlist_items):
        self.logger.info('updating `Songs` table')

        for playlist_id in playlist_items:
            for item in playlist_items[playlist_id]:
                sql = f"""
                    INSERT OR IGNORE INTO Songs (
                        video_id, video_name, playlist_id, able_to_download
                    ) VALUES (?, ?, ?, 1);
                """
                self.db.execute(sql, [item['contentDetails']['videoId'], item['snippet']['title'], playlist_id])


    def fetch_new_playlist_items(self):
        # gets a list of all items in the playlists, and then uses the db to only insert info about the new items into the db
        if not self.args.skip_api:
            if not self.args.playlist_ids:
                playlists = self.get_stored_playlist_ids()
            else:
                playlists = self.args.playlist_ids

            self.api.validate_playlists(playlists)

            playlists = self.api.get_playlists()
            self.merge_playlists(playlists)

            playlist_items = self.api.get_playlist_items()
            self.merge_songs(playlist_items)

            self.logger.info('successfully fetched all items from YouTube')


    def download_items(self):
        # gets a list of all items in the db that don't have a download location populated for the mounted usb drive and downloads straight to the usb drive
        # updates db afterward
        if not self.args.skip_download:
            devices = self.usb.scan()
            for device in devices:
                self.downloader.download_songs(device)


    def main(self):
        try:
            self.logger.info('starting downloader')

            self.fetch_new_playlist_items()
            self.download_items()
            self.logger.info('completed successfully')

        except Exception as e:
            self.logger.error(e)
            sys.exit(0)

        finally:
            self.db.disconnect()


if __name__ == "__main__":
    md = MusicDownloader()
    md.main()

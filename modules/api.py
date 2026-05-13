import requests
import os
import sys
from dotenv import load_dotenv


class API:
    def __init__(self, logger, db):
        self.logger = logger
        self.db = db

        self.base_url = "https://www.googleapis.com/youtube/v3/"

        self.playlists = []
        self.video_ids = {}  # key = playlist_id, value = list of video_ids

        self.__get_token()


    def __get_token(self):
        load_dotenv()
        self.token = os.getenv('TOKEN')


    def validate_playlists(self, playlists):
        self.logger.info('validating playlists')

        url = self.base_url + 'playlists'

        params = {
            'part': 'id,snippet',
            'id': playlists,
            'key': self.token
        }

        self.logger.info('getting playlist information from YouTube API...')
        response = requests.get(url, params=params)
        data = response.json()

        self.logger.info(f'{len(data["items"])} playlists were identified:')

        if len(data['items']) == 0:
            self.logger.info('no playlists identified, exiting')
            sys.exit(0)

        for playlist in data['items']:
            self.logger.info(f' * {playlist["snippet"]["title"]} ({playlist["id"]})')
        self.logger.info('')

        user_input = input('are you sure that you want to continue? (y/n) ')
        if not user_input == 'y':
            self.logger.info('exiting')
            sys.exit(0)

        self.playlists = data['items']


    def get_playlists(self):
        return self.playlists


    def get_playlist_items(self):
        self.logger.info('fetching playlist items...')

        url = self.base_url + 'playlistItems'

        for playlist in self.playlists:
            params = {
                "part": "snippet,contentDetails",
                "playlistId": playlist['id'],
                "maxResults": 50,
                "key": self.token
            }

            video_ids_in_current_playlist = []
            next_page_token = None

            while True:
                if next_page_token:
                    params['pageToken'] = next_page_token

                response = requests.get(url, params=params)
                data = response.json()

                video_ids_in_current_playlist.extend(data.get('items', []))

                next_page_token = data.get("nextPageToken")
                if not next_page_token:
                    break

            self.video_ids[playlist['id']] = video_ids_in_current_playlist

        return self.video_ids

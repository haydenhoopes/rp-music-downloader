import requests


class API:
    def __init__(self):
        self.token = "AIzaSyCfYXmCeqDdhVLwkL3oPu0flFPpb9415vI"
        self.base_url = "https://www.googleapis.com/youtube/v3/playlistItems"
        self.playlist_id = "PLU0hyGoSZN9DRmK8AnZ6amj_NNwYUpWyx"
        self.videos = []

    def get_items(self):
        if len(self.videos) == 0:
            next_page_token = None

            while True:
                params = {
                    "part": "snippet",
                    "playlistId": self.playlist_id,
                    "maxResults": 50,  # Maximum number of items that can be retrieved per page
                    "pageToken": next_page_token,
                    "key": self.token
                }

                response = requests.get(self.base_url, params=params)
                data = response.json()

                for item in data["items"]:
                    video_id = item["snippet"]["resourceId"]["videoId"]
                    video_title = item["snippet"]["title"]
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    self.videos.append({"id": video_id, "title": video_title, "url": video_url})

                next_page_token = data.get("nextPageToken")
                if not next_page_token:
                    break

        return self.videos

    def get_item_count(self):
        return len(self.get_items())
    
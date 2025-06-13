from pytube import YouTube
import subprocess, os
from wasabi import msg


class Downloader:
    def __init__(self):
        self.output_dir = '/rp_music'

    def download(self, item, path):
        yt = YouTube(item['url'])
        audio_stream = yt.streams.filter(only_audio=True).first()
        path = path + self.output_dir
        audio_file_path = audio_stream.download(output_path=path)
        base, ext = os.path.splitext(audio_file_path)
        new_file = base + ".mp3"

        subprocess.run(['ffmpeg', '-i', audio_file_path, new_file])

        os.remove(audio_file_path)
        msg.info(f'item {item["name"]} downloaded')

    def download_items(self, items, mount_path):
        for item in items:
            self.download(item, mount_path)

    def set_device(self, device):
        self.mount_point = device[1]

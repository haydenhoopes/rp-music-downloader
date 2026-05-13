from pytubefix import YouTube
import subprocess
import os
from datetime import datetime



class Downloader:
    def __init__(self, logger, db):
        self.logger = logger
        self.db = db


    def download(self, device, video_ids, playlist_name):
        """
        Downloads a list of video IDs directly to the USB drive
        in a folder named after the playlist.
        Converts each to MP3 using ffmpeg.
        """
        # Create folder for this playlist on the USB root
        playlist_folder = os.path.join(device.drive_letter + "\\", playlist_name)
        os.makedirs(playlist_folder, exist_ok=True)

        for video_id in video_ids:
            try:
                video_id = video_id.strip()
                url = f"https://www.youtube.com/watch?v={video_id}"

                yt = YouTube(url)

                audio_stream = yt.streams.get_audio_only()

                # Download directly to USB playlist folder
                audio_file_path = audio_stream.download(output_path=playlist_folder)

                base, ext = os.path.splitext(audio_file_path)
                mp3_file = base + ".mp3"

                subprocess.run(
                    ['ffmpeg', '-y', '-i', audio_file_path, mp3_file],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,  # hides all messages
                    check=True
                )
                # Remove the original downloaded file
                os.remove(audio_file_path)

                self.logger.info(f"Downloaded '{yt.title}' to {playlist_name}")
                self.__update_usb_songs(device, video_id)

            except Exception as e:
                self.logger.error(f"Failed to download {video_id}: {e}")
                self.__song_cannot_be_downloaded(video_id)


    def __update_usb_songs(self, device, video_id):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sql = """
            INSERT INTO USB_Songs (
                video_id, volume_name, date_downloaded
            ) VALUES (?, ?, ?);
        """
        self.db.execute(sql, [video_id, device.volume_name, now])


    def __song_cannot_be_downloaded(self, video_id):
        sql = """
            UPDATE Songs
            SET able_to_download = 0
            WHERE
                video_id = ?;
        """
        self.db.execute(sql, [video_id])


    def __get_songs_to_download_for_device(self, device):
        sql = """
            SELECT
                s.video_id,
                p.playlist_name
            FROM
                Songs s
            INNER JOIN
                Playlists p ON
                    s.playlist_id = p.playlist_id
            LEFT JOIN
                USB_Songs us ON
                    s.video_id = us.video_id
                    AND us.volume_name = ?
            WHERE
                us.video_id IS NULL
                AND s.able_to_download = 1;
        """
        return self.db.execute(sql, [device.volume_name])


    def download_songs(self, device):
        self.logger.info(f'downloading songs for {device.volume_name} ({device.drive_letter})')

        songs_to_download = self.__get_songs_to_download_for_device(device)
        self.logger.info(f'found {len(songs_to_download)} songs to download')

        playlist_songs = {}

        for row in songs_to_download:
            if row[1] in playlist_songs:
                playlist_songs[row[1]].append(row[0])
            else:
                playlist_songs[row[1]] = [row[0]]

        for playlist in playlist_songs.keys():
            self.download(device, playlist_songs[playlist], playlist)

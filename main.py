#!/usr/local/bin/python


from usb import USB
from db import Database
from api import API
from downloader import Downloader


def main(api, db, usb):
    downloader = Downloader()

    db.create_table()
    
    api_items = api.get_items()
    items_to_download = db.get_items_that_havent_been_downloaded_yet(api_items)

    # Download stuff
    usb.mount()
    downloader.set_device(usb.get_usb())
    downloader.download_items(items_to_download)
    db.add_downloaded_items(items_to_download)
    usb.eject()

if __name__ == "__main__":
    usb = USB()
    db = Database()
    api = API()

    if usb.exists():
        if api.get_item_count() != db.get_item_count():
            main(api, db, usb)
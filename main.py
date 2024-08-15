#!/usr/local/bin/python


from usb import USB
from db import Database
from api import API
from downloader import Downloader
from datetime import datetime
from wasabi import msg


def main(api, db, usb):
    try:
        downloader = Downloader()

        api_items = api.get_items()
        print('connected to api')

        items_to_download = db.get_items_that_havent_been_downloaded_yet(api_items)
        msg.info(f'{len(items_to_download)} items to download')

        # Download stuff
        usb.mount()

        downloader.download_items(items_to_download, usb.get_path())
        msg.good('items downloaded successfully')

        db.add_downloaded_items(items_to_download)

        usb.eject()
    except Exception as e:
        msg.fail(e)

if __name__ == "__main__":
    msg.info(f'starting downloader: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    usb = USB()
    db = Database()
    api = API()

    if usb.exists():
        db.create_table()
        print('connected to db')
        usb_serial_number = usb.get_serial_number()
        if api.get_item_count() != db.get_item_count(usb_serial_number):
            main(api, db, usb)
        else:
            print('no new items to download')
    else:
        print('no usb inserted')
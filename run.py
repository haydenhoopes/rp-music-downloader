#!/usr/local/bin/python


from modules.usb import USB
from modules.db import Database
from modules.api import API
from modules.downloader import Downloader
from modules.logger import Logger


def main():
    logger = Logger()
    usb = USB(logger)

    usb.mount_all()

    return


    try:
        msg = Printer(timestamp=True)

        msg.info(f' starting downloader')
        usb = USB()
        db = Database()
        api = API()

        if usb.exists():
            db.create_table()
            msg.info(' connected to db')
            usb_serial_number = usb.get_serial_number()
            if api.get_item_count() != db.get_item_count(usb_serial_number):
                msg.info(api, db, usb)
            else:
                msg.info(' no new items to download')
        else:
            msg.info(' no usb inserted')

        downloader = Downloader()

        api_items = api.get_items()

        items_to_download = db.get_items_that_havent_been_downloaded_yet(api_items)
        msg.info(f' {len(items_to_download)} items to download')

        # Download stuff
        usb.mount()

        downloader.download_items(items_to_download, usb.get_path())
        msg.good('items downloaded successfully')

        db.add_downloaded_items(items_to_download)

        usb.eject()
    except Exception as e:
        msg.fail(e)


if __name__ == "__main__":
    main()


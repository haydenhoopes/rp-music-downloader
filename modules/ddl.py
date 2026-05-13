# Data Model (tables)
#  - USB: contains a list of all USB sticks that have been used with the project
#  - Songs: contains a list of songs that have been identified from the target playlists
#  - USB_Songs: contains a list of the songs that were downloaded to a USB stick, and the file location


class DDL:
    def __init__(self, logger, db):
        self.logger = logger
        self.db = db


    def __create_table__usb(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS USB (
                volume_name      VARCHAR(255),
                size             REAL,
                UNIQUE(volume_name)
            );
        """
        self.db.execute(sql)
        self.logger.info('table `USB` created')


    def __create_table__songs(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS Songs (
                video_id             VARCHAR(255),
                video_name           VARCHAR(255),
                playlist_id          VARCHAR(255),
                title                VARCHAR(255),
                artist               VARCHAR(255),
                able_to_download   TINYINT,
                UNIQUE(video_id)
            );
        """
        self.db.execute(sql)
        self.logger.info('table `Songs` created')


    def __create_table__usb_songs(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS USB_Songs (
                video_id         VARCHAR(255),
                volume_name      VARCHAR(255),
                date_downloaded  TIMESTAMP,
                UNIQUE(video_id, volume_name)
            );
        """
        self.db.execute(sql)
        self.logger.info('table `USB_Songs` created')


    def __create_table__playlists(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS Playlists (
                playlist_id      INTEGER,
                playlist_name    INTEGER,
                UNIQUE (playlist_id)
            );
        """
        self.db.execute(sql)
        self.logger.info('table `Playlists` created')


    def __drop_tables(self):
        self.db.execute('drop table USB;')
        self.db.execute('drop table Songs;')
        self.db.execute('drop table USB_Songs;')
        self.db.execute('drop table Playlists;')
        self.logger.info('database reset')


    def execute(self, args):
        if args.reset:
            self.__drop_tables()

        self.__create_table__usb()
        self.__create_table__songs()
        self.__create_table__usb_songs()
        self.__create_table__playlists()
        self.logger.info('ddl complete')

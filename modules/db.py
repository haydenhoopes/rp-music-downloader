import sqlite3


class Database:
    def __init__(self, logger):
        self.database_name = 'rp_music_downloader.db'
        self.results = None
        self.connection = None
        self.logger = logger


    def connect(self):
        if not self.connection:
            self.connection = sqlite3.connect(self.database_name, isolation_level=None)  # auto commits
            self.cursor = self.connection.cursor()
            self.logger.info('connected to db')


    def execute(self, sql, params=[]):
        self.connect()
        self.cursor.execute(sql, params)
        results = self.cursor.fetchall()
        return results


    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            self.logger.info('disconnected from db')

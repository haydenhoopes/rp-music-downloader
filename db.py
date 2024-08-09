import sqlite3


class Database:
    def __init__(self):
        self.database_name = 'items.db'
        self.results = None
        self.items_to_download = None
        
    def connect(self):
        self.connection = sqlite3.connect(self.database_name)
        self.cursor = self.connection.cursor()

    def execute(self, sql):
        self.connect()
        self.cursor.execute(sql)

    def commit(self, sql):
        self.execute(sql)
        self.connection.commit()

    def create_table(self):
        sql = """
            CREATE TABLE IF NOT EXISTS items (
                video_id VARCHAR(100) PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                url VARCHAR(150) NOT NULL
            );
        """
        self.commit(sql)

    def get_items(self):
        if not self.results:
            sql = """
                SELECT video_id, name, url
                FROM items
                ;
            """
            self.execute(sql)
            self.results = self.cursor.fetchall()
        return self.results
    
    def item_already_downloaded(self, item):
        for result in self.results:
            if item['id'] == result[0]:
                return True
        return False
        
    def get_items_that_havent_been_downloaded_yet(self, api_items):
        if not self.items_to_download:
            self.items_to_download = []
            for item in api_items:
                if not self.item_already_downloaded(item):
                    self.items_to_download.append(item)
        return self.items_to_download

    def get_item_count(self):
        return len(self.get_items())
        
    def add_downloaded_item(self, video_id, name, url):
        sql = f"""
            INSERT INTO items (
                video_id, name, url
            ) VALUES (
                '{video_id}',
                '{name}',
                '{url}'
            );
        """
        self.commit(sql)

    def add_downloaded_items(self, items):
        for item in items:
            self.add_downloaded_item(item['id'], item['name'], item['url'])
import datetime
import sqlite3
import logging
import time
from pathlib import Path
from sqlite3 import Error


def adapt_datetime(ts):
    return time.mktime(ts.timetuple())


class DatabaseWrapper():

    def __init__(self):
        self.dbfile_path = Path.cwd().joinpath('database', 'user_data.db')

        self.connection = None
        self.cursor = None

        self.logger = logging.getLogger('database')
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(filename='database/database.log', encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        self.logger.addHandler(handler)

    def create_connection(self) -> None:
        """Creates connection if no other instance has been created."""
        if self.connection is None:
            try:
                if self.dbfile_path.exists():
                    self.logger.info(__name__ + ': Existing database found. Connecting...')
                else:
                    self.logger.info(__name__ + ': Existing database not found. Creating new db file.')
                self.connection = sqlite3.connect(self.dbfile_path, detect_types=sqlite3.PARSE_DECLTYPES)
                sqlite3.register_adapter(datetime.datetime, adapt_datetime)
                self.cursor = self.connection.cursor()
                self.cursor.execute("PRAGMA foreign_keys = 1")
                self.logger.info("Opened up a database using SQLite3 Version: " + sqlite3.sqlite_version)
            except Error as e:
                print(e)

    def close_connection(self) -> None:
        """Closes the connection for the instance."""
        self.connection.close()

    def execute(self, statement: str):
        try:
            result = self.cursor.execute(statement)
            self.connection.commit()
            return result
        except Error as e:
            self.logger.error(e)

    def commit(self):
        try:
            self.connection.commit()
        except Error as e:
            self.logger.error(e)

    def create_table(self, statement):
        try:
            self.execute(statement)
        except Error as e:
            self.logger.error(e)

    def __enter__(self):
        self.create_connection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()

    def __del__(self):
        pass

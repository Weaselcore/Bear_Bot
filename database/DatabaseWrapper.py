import sqlite3
import logging

from pathlib import Path
from sqlite3 import Error


class DatabaseWrapper:

    def __init__(self):
        self.dbfile_path = Path.cwd().joinpath('database', 'user_data.db')
        self.connection = None
        self.cursor = None
        self.logger = logging.getLogger('discord')
        self.create_connection()

    def create_connection(self) -> None:
        """Creates connection if no other instance has been created."""
        if self.connection is None:
            try:
                if self.dbfile_path.exists():
                    self.logger.info(__name__ + ': Existing database found. Connecting...')
                else:
                    self.logger.info(__name__ + ': Existing database not found. Creating new db file.')
                self.connection = sqlite3.connect(self.dbfile_path, detect_types=sqlite3.PARSE_DECLTYPES)
                self.cursor = self.connection.cursor()
                self.execute("PRAGMA foreign_keys = 1")
                self.logger.info("Opened up a database using SQLite3 Version: " + sqlite3.sqlite_version)
            except Error as e:
                print(e)

    def close_connection(self) -> None:
        """Closes the connection for the instance."""
        self.connection.close()

    def execute(self, statement):
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

    def create_table(self, statement) -> None:
        try:
            self.execute(statement)
        except Error as e:
            self.logger.error(e)

import sqlite3
import logging

from BBLibrary.Singleton import Singleton
from pathlib import Path
from sqlite3 import Error


class DatabaseWrapper(Singleton):
    def __init__(self):
        self.dbfile_path = Path.cwd().joinpath('database', 'user_data.db')
        self.connection = None
        self.logger = logging.getLogger('discord')
        self.create_connection()

    def create_connection(self) -> None:
        """Creates connection if no other instance has benn created."""
        if self.connection is None:
            try:
                if self.dbfile_path.exists():
                    self.logger.info(__name__ + ': Existing database found. Connecting...')
                else:
                    self.logger.info(__name__ + ': Existing database not found. Creating new db file.')
                self.connection = sqlite3.connect(self.dbfile_path)
            except Error as e:
                print(e)
            finally:
                if self.connection:
                    self.connection.close()


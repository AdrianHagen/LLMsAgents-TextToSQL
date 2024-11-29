import sqlite3
from sqlite3 import Connection
from threading import Lock
import os
import timeit
from typing import Tuple


def list_databases() -> list:
    databases = []
    db_directory = os.getenv("DB_DIRECTORY")
    for root, dirs, files in os.walk(db_directory):
        for file in files:
            if file.endswith(".sqlite"):
                databases.append(os.path.join(root, file))
    db_list = []
    for db in databases:
        db_name = os.path.splitext(os.path.basename(db))[0]
        db_list.append({"name": db_name, "path": db})
    return db_list


import sqlite3
from sqlite3 import Connection
from threading import Lock
import os
import timeit
from typing import Tuple


class Database:
    _connection_pool = {}  # Shared pool for database connections
    _lock = Lock()  # Lock for thread-safe access to the connection pool

    def __init__(self, name: str):
        self.name = name
        self.path = self.get_db_path()

    def get_db_path(self) -> str:
        databases = list_databases()
        for db in databases:
            if db["name"] == self.name:
                return db["path"]
        raise ValueError(f"Database with name {self.name} not found.")

    def get_connection(self) -> Connection:
        with self._lock:
            # Check if the connection for this database already exists
            if self.path not in self._connection_pool:
                # Create a new connection if not already present
                self._connection_pool[self.path] = sqlite3.connect(self.path)
            return self._connection_pool[self.path]

    def execute_query(self, query: str, params: tuple = ()) -> Tuple[list, float]:
        conn = self.get_connection()
        cursor = conn.cursor()
        start_time = timeit.default_timer()
        cursor.execute(query, params)

        results = cursor.fetchall()
        cursor.close()

        execution_time = timeit.default_timer() - start_time

        return (results, execution_time)

    @classmethod
    def close_all_connections(cls):
        with cls._lock:
            # Close all connections in the pool
            for conn in cls._connection_pool.values():
                conn.close()
            cls._connection_pool.clear()

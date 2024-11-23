import sqlite3
from sqlite3 import Connection
from threading import Lock
import os


def list_databases() -> list:
    databases = []
    db_directory = os.getenv("DB_DIRECTORY")
    for root, dirs, files in os.walk(db_directory):
        for file in files:
            if file.endswith('.sqlite'):
                databases.append(os.path.join(root, file))
    db_list = []
    for db in databases:
        db_name = os.path.splitext(os.path.basename(db))[0]
        db_list.append({"name": db_name, "path": db})
    return db_list

class SingletonMeta(type):
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]

class Database(metaclass=SingletonMeta):
    def __init__(self, name: str):
        self.name = name
        self.path = self._get_db_path(name)
        self.connection = None

    def _get_db_path(self, name: str) -> str:
        databases = list_databases()
        for db in databases:
            if db["name"] == name:
                return db["path"]
        raise ValueError(f"Database with name {name} not found.")

    def get_connection(self) -> Connection:
        if self.connection is None:
            self.connection = sqlite3.connect(self.path)
        return self.connection

    def execute_query(self, query: str, params: tuple = ()) -> list:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        return results
        


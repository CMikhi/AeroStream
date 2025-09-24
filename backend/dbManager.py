# dbManager.py
import sqlite3
from sqlite3 import Error
import os
from typing import List, Tuple, Any, Optional

class DatabaseManager:
    def __init__(self, db_file: str):
        """Initialize with an absolute path to the database file (no persistent connection)."""
        self.db_file = os.path.abspath(db_file)
        self._tables_created = False

    def _connect(self) -> sqlite3.Connection:
        """
        Create and return a fresh sqlite3.Connection.
        Each thread/request uses it's own connection as SQLite is NOT thread-safe
        """
        # check_same_thread=False is not required for per-connection usage but harmless.
        conn = sqlite3.connect(self.db_file, timeout=30, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # optional: access columns by name
        # Set recommended pragmas for better concurrency and foreign keys
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def create_connection(self):
        """
        Create the DB file if it doesn't exist and verify we can open it.
        This does NOT keep a long-lived connection.
        Also creates required tables if they don't exist.
        """
        try:
            created = not os.path.exists(self.db_file)
            conn = self._connect()
            conn.close()
            if created:
                print(f"Created new database file: {self.db_file}")
            print(f"Connection to SQLite DB '{self.db_file}' successful.")
            
            # Create tables after successful connection
            if not self._tables_created:
                self._create_tables()
                self._tables_created = True
        except Error as e:
            print(f"Error connecting to database: {e}")

    def _create_tables(self):
        """Create the required tables for the chat application."""
        # Create tables for users, rooms, and messages
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );
        """

        create_rooms_table = """
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_key TEXT NOT NULL UNIQUE,
            created_by INTEGER,
            private BOOLEAN NOT NULL DEFAULT FALSE,
            password TEXT CHECK(private != FALSE OR password IS NULL),
            FOREIGN KEY (created_by) REFERENCES users (id)
        );
        """

        create_messages_table = """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            room_id INTEGER,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (room_id) REFERENCES rooms (id)
        );
        """

        print("Creating database tables...")
        self.create_table(create_users_table, silent=True)
        self.create_table(create_rooms_table, silent=True)
        self.create_table(create_messages_table, silent=True)
        print("Database tables created successfully.")

    def create_table(self, create_table_sql: str, silent: bool = False):
        """Create a table using the provided SQL statement (safe per-op connection)."""
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute(create_table_sql)
                # conn.commit() happens automatically on context manager exit if no exception
                if not silent:
                    print("Table created successfully.")
        except Error as e:
            print(f"Error creating table: {e}")

    def execute_query(self, query: str, params: Optional[Tuple[Any, ...]] = None):
        """Execute a query with optional parameters in a fresh connection."""
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                if params:
                    cur.execute(query, params)
                else:
                    cur.execute(query)
                # commit on context exit
                print("Query executed successfully.")
        except Error as e:
            print(f"Error executing query: {e}")

    def push_data(self, table: str, data: Tuple[Any, ...]):
        """Insert data into a specified table. 'data' should be a tuple of values matching table columns."""
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO {table} VALUES ({placeholders})"
        self.execute_query(query, data)

    def fetch_all(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> List[sqlite3.Row]:
        """Fetch all rows for a given query and return a list of sqlite3.Row (can be converted to dict)."""
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                if params:
                    cur.execute(query, params)
                else:
                    cur.execute(query)
                rows = cur.fetchall()
                return rows
        except Error as e:
            print(f"Error fetching data: {e}")
            return []

    def close_connection(self):
        """
        Kept for API parity; nothing to close because we open per-operation connections.
        This is a no-op but left to avoid breaking code that calls it.
        """
        print("DatabaseManager uses per-operation connections; nothing to close.")

# Example usage (keep as script for initial DB creation)
if __name__ == "__main__":
    # WARNING: THIS WILL RESET the DB file creation step below if you truncate it.
    # Create (or truncate) a db file for demonstration
    with open("database.db", "wb"):
        pass

    db_manager = DatabaseManager("database.db")
    db_manager.create_connection()

    # Create tables for users, rooms, and messages
    create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    );
    """

    create_rooms_table = """
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_key TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        created_by INTEGER,
        FOREIGN KEY (created_by) REFERENCES users (id)
    );
    """

    create_messages_table = """
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        room_id INTEGER,
        content TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (room_id) REFERENCES rooms (id)
    );
    """

    db_manager.create_table(create_users_table)
    db_manager.create_table(create_rooms_table)
    db_manager.create_table(create_messages_table)

    db_manager.execute_query("INSERT INTO users (username, password) VALUES (?, ?)", ("John Doe", "password123"))
    users = db_manager.fetch_all("SELECT * FROM users")
    # convert sqlite3.Row objects to tuples or dicts for printing
    print([dict(row) for row in users])

    db_manager.close_connection()

import sqlite3
from sqlite3 import Error

class DatabaseManager:
    def __init__(self, db_file):
        """Initialize the DatabaseManager with the database file."""
        self.db_file = db_file
        self.connection = None

    def create_connection(self):
        """Create a database connection to the SQLite database."""
        try:
            self.connection = sqlite3.connect(self.db_file)
            print(f"Connection to SQLite DB '{self.db_file}' successful.")
        except Error as e:
            print(f"Error connecting to database: {e}")

    def create_table(self, create_table_sql):
        """Create a table using the provided SQL statement."""
        try:
            if self.connection is not None:
                cursor = self.connection.cursor()
                cursor.execute(create_table_sql)
                print("Table created successfully.")
            else:
                print("No database connection.")
        except Error as e:
            print(f"Error creating table: {e}")

    def execute_query(self, query, params=None):
        """Execute a query with optional parameters."""
        try:
            if self.connection is not None:
                cursor = self.connection.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                self.connection.commit()
                print("Query executed successfully.")
            else:
                print("No database connection.")
        except Error as e:
            print(f"Error executing query: {e}")

    def fetch_all(self, query, params=None):
        """Fetch all rows for a given query."""
        try:
            if self.connection is not None:
                cursor = self.connection.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.fetchall()
            else:
                print("No database connection.")
        except Error as e:
            print(f"Error fetching data: {e}")
            return []

    def close_connection(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")

# Example usage:
if __name__ == "__main__":
    db_manager = DatabaseManager("example.db")
    db_manager.create_connection()

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        email TEXT
    );
    """
    db_manager.create_table(create_table_sql)

    db_manager.execute_query("INSERT INTO users (name, age, email) VALUES (?, ?, ?)", ("John Doe", 30, "john@example.com"))
    users = db_manager.fetch_all("SELECT * FROM users")
    print(users)

    db_manager.close_connection()
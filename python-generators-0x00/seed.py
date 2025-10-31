#!/usr/bin/python3
"""
seed.py

Sets up MySQL database `ALX_prodev` and table `user_data`.
Populates the table from a CSV file and demonstrates a generator
that streams database rows one by one.

Concepts Demonstrated:
- Generators for streaming database rows.
- Context Managers for managing database connections and cursors.
- Clean modular functions for database setup.

Author: Ayman
Repository: alx-backend-python
Directory: python-generators-0x00
"""

import mysql.connector
from mysql.connector import Error
import csv
import uuid
from contextlib import contextmanager


# ----------------------------------------------------------
# Context Manager: Database Connection
# ----------------------------------------------------------
@contextmanager
def db_connection(host="localhost", user="root", password="*!eR5$fr8RN3Fb", database=None):
    """
    Context manager to handle MySQL database connections.
    Automatically closes the connection when done.
    """
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        yield connection
    except Error as e:
        print(f"[ERROR] Database connection error: {e}")
        yield None
    finally:
        if connection and connection.is_connected():
            connection.close()


# ----------------------------------------------------------
# 1 Connect to MySQL Server (no database yet)
# ----------------------------------------------------------
def connect_db():
    """Connect to the MySQL server (without database)."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="*!eR5$fr8RN3Fb"  # ← Replace with your MySQL root password
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"[ERROR] Cannot connect to MySQL server: {e}")
        return None


# ----------------------------------------------------------
# 2 Create the Database
# ----------------------------------------------------------
def create_database(connection):
    """Create the database ALX_prodev if it does not exist."""
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev;")
        cursor.close()
        print("Database ALX_prodev created or already exists.")
    except Error as e:
        print(f"[ERROR] Creating database failed: {e}")


# ----------------------------------------------------------
# 3 Connect to the ALX_prodev Database
# ----------------------------------------------------------
def connect_to_prodev():
    """Connect directly to ALX_prodev database."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="*!eR5$fr8RN3Fb",  # ← Replace with your MySQL root password
            database="ALX_prodev"
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"[ERROR] Cannot connect to ALX_prodev: {e}")
        return None


# ----------------------------------------------------------
# 4 Create the user_data Table
# ----------------------------------------------------------
def create_table(connection):
    """Create the user_data table if it does not exist."""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS user_data (
        user_id CHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        age DECIMAL(3,0) NOT NULL,
        INDEX (user_id)
    );
    """
    try:
        cursor = connection.cursor()
        cursor.execute(create_table_query)
        connection.commit()
        cursor.close()
        print("Table user_data created successfully.")
    except Error as e:
        print(f"[ERROR] Creating table failed: {e}")


# ----------------------------------------------------------
# 5 Insert Data from CSV
# ----------------------------------------------------------
def insert_data(connection, csv_file):
    """Insert data into the user_data table from a CSV file."""
    try:
        cursor = connection.cursor()
        with open(csv_file, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                user_id = str(uuid.uuid4())
                name = row.get("name")
                email = row.get("email")
                age = row.get("age")

                cursor.execute("""
                    INSERT INTO user_data (user_id, name, email, age)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, name, email, age))

        connection.commit()
        cursor.close()
        print("Data inserted successfully from CSV.")
    except FileNotFoundError:
        print(f"[ERROR] CSV file '{csv_file}' not found.")
    except Error as e:
        print(f"[ERROR] Inserting data failed: {e}")


# ----------------------------------------------------------
# 6 Generator: Stream Rows from Database
# ----------------------------------------------------------
def stream_rows(connection, batch_size=1):
    """
    Generator that yields rows from user_data table one by one.

    Args:
        connection: Active MySQL connection
        batch_size: Number of rows fetched per iteration (default 1)
    Yields:
        Each row from the table.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user_data;")
        while True:
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break
            for row in rows:
                yield row
        cursor.close()
    except Error as e:
        print(f"[ERROR] Streaming rows failed: {e}")
        return


# ----------------------------------------------------------
# Optional: Demonstration when run directly
# ----------------------------------------------------------
if __name__ == "__main__":
    print("🔹 Connecting to MySQL server...")
    connection = connect_db()
    if connection:
        create_database(connection)
        connection.close()
        print("✅ Connection successful and database verified.\n")

        print("🔹 Connecting to ALX_prodev...")
        connection = connect_to_prodev()

        if connection:
            create_table(connection)
            insert_data(connection, "user_data.csv")

            print("\n🔹 Streaming first few rows:")
            for i, row in enumerate(stream_rows(connection)):
                print(row)
                if i == 4:
                    break
            connection.close()

import sqlite3
from pathlib import Path

import markupsafe

from __init__ import logger, MOCK_DATA, DATABASE

# We want to use the same exceptions as the database module
IntegrityError = sqlite3.IntegrityError


# Context manager for database connection
# TODO: A lot needs to be done here - we want to move away from sqlite3 and use a dedicated database server
class connect:
    def __init__(self, commit_on_close=True) -> None:
        self.con = sqlite3.connect(DATABASE)
        self.cur = self.con.cursor()
        self.commit_on_close = commit_on_close

    def __enter__(self) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
        return self.con, self.cur

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.commit_on_close:
            self.con.commit()
        self.con.close()


def read_sql_query(sql_name) -> str:
    return Path(f'{Path(__file__).parent}/sql/{sql_name}').read_text()


def add_admin(data_dict: dict) -> None:
    """Add an admin to the database with the given data (less information than a normal user)."""
    with connect() as (con, cur):
        cur.execute(read_sql_query("add_admin.sql"), data_dict)
    logger.info(f'Added admin {data_dict["name"]} to database. ({data_dict["userid"]})')


def init_db() -> None:
    """Create the database and tables if they don't exist."""
    with connect() as (con, cur):
        [cur.execute(query) for query in read_sql_query("tables.sql").split(';')]

    if MOCK_DATA:
        logger.info('MOCK_DATA is enabled. Recreating mock data.')
        create_mock_data()


def create_mock_data() -> None:
    """Clear the relevant databases and add fresh mock data"""
    with connect() as (con, cur):
        cur.execute('DELETE FROM users')
        cur.execute('DELETE FROM inventory')
        cur.execute('DELETE FROM audits')
        [cur.execute(query) for query in read_sql_query("mock_data.sql").split(';')]


class Settings:
    @staticmethod
    def get(key: str) -> str:
        """Get a setting by key."""
        with connect() as (con, cur):
            cur.execute('SELECT value FROM settings WHERE name = ?', (key,))
            value = cur.fetchone()

        return markupsafe.Markup(value[0]) if value else ''

    @staticmethod
    def set(key: str, value: str) -> None:
        """Set a setting by key."""
        with connect() as (con, cur):
            cur.execute('REPLACE INTO settings (name, value) VALUES (?, ?)', (key, value))

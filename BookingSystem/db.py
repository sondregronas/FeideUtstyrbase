import sqlite3
from pathlib import Path

from __init__ import DATABASE, logger


def read_sql_query(sql_name) -> str:
    return Path(f'sql/{sql_name}').read_text()


def add_admin(data_dict: dict) -> None:
    """Add an admin to the database with the given data (less information than a normal user)."""
    con = sqlite3.connect(DATABASE)
    con.execute(read_sql_query("add_admin.sql"), data_dict)
    con.commit()
    con.close()
    logger.info(f'Added admin {data_dict["name"]} to database. ({data_dict["userid"]})')


def get_user(userid: str) -> dict:
    """Load the user's information from the database."""
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute(read_sql_query("get_user_by_id.sql"), (userid,))
    user = cur.fetchone()
    columns = [description[0] for description in cur.description]
    con.close()
    if not user:
        return {}
    return {columns[i]: user[i] for i in range(len(columns))}


def init_db() -> None:
    con = sqlite3.connect(DATABASE)
    con.executescript(read_sql_query("tables.sql"))
    con.close()

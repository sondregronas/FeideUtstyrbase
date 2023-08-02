import sqlite3

from __init__ import DATABASE


def get_all() -> list[str]:
    """Return a list of all groups in the database."""
    con = sqlite3.connect(DATABASE)
    groups = [row[0] for row in con.execute('SELECT classroom FROM groups ORDER BY classroom ASC')]
    con.close()
    return groups

import sqlite3

import flask

from BookingSystem import DATABASE

groups = flask.Blueprint('groups', __name__)


def get_all() -> list[str]:
    """Return a list of all groups in the database."""
    con = sqlite3.connect(DATABASE)
    groups = [row[0] for row in con.execute('SELECT classroom FROM groups ORDER BY classroom ASC')]
    con.close()
    return groups


def get_all_emails() -> list[str]:
    """Return a list of all emails in the database."""
    con = sqlite3.connect(DATABASE)
    emails = [row[0] for row in con.execute('SELECT email FROM emails ORDER BY email ASC')]
    con.close()
    return emails

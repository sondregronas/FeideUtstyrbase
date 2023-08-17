import sqlite3
from datetime import datetime

from dateutil import parser
from markupsafe import Markup

from __init__ import DATABASE


def audit(event: str, message: str) -> None:
    """Log an event to the database. (Max 10k entries before replacing older entries)"""
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    sql = 'INSERT INTO audits (timestamp, event, message) VALUES (:timestamp, :event, :message)'
    cur.execute(sql, {
        'timestamp': datetime.now(),
        'event': event,
        'message': message
    })
    sql = 'SELECT COUNT(*) FROM audits'
    cur.execute(sql)
    if cur.fetchone()[0] > 10_000:
        sql = 'DELETE FROM audits WHERE id IN (SELECT id FROM audits ORDER BY id ASC LIMIT 1)'
        cur.execute(sql)
    con.commit()
    con.close()


def get_all() -> list[dict]:
    """Get the logs from the audit log."""
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    sql = 'SELECT * FROM audits ORDER BY id DESC'
    cur.execute(sql)
    rows = cur.fetchall()
    con.close()
    return [{
        'timestamp': parser.parse(row[1]).strftime('%d.%m.%Y %H:%M:%S'),
        'event': row[2],
        'message': Markup(row[3]).unescape()
    } for row in rows]

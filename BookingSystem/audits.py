from datetime import datetime

from dateutil import parser
from markupsafe import Markup

import db


def audit(event: str, message: str) -> None:
    """Log an event to the database. (Max 10k entries before replacing older entries)"""
    with db.connect() as (con, cur):
        sql = 'INSERT INTO audits (timestamp, event, message) VALUES (:timestamp, :event, :message)'
        cur.execute(sql, {
            'timestamp': datetime.now(),
            'event': event,
            'message': message
        })
        sql = 'SELECT COUNT(*) FROM audits'
        cur.execute(sql)
        if cur.fetchone()[0] > 10_000:  # pragma: no cover
            sql = 'DELETE FROM audits WHERE id IN (SELECT id FROM audits ORDER BY id ASC LIMIT 1)'
            cur.execute(sql)


def get_all() -> list[dict]:
    """Get the logs from the audit log."""
    with db.connect() as (con, cur):
        sql = 'SELECT * FROM audits ORDER BY id DESC'
        cur.execute(sql)
        rows = cur.fetchall()

    return [{
        'timestamp': parser.parse(row[1]).strftime('%d.%m.%Y %H:%M:%S'),
        'event': row[2],
        'message': Markup(row[3]).unescape()
    } for row in rows]


def get_new_deviations(since: float | int | str) -> list:
    """Return a list of new deviations."""
    return [a['message'] for a in get_all()
            if parser.parse(a['timestamp']) > datetime.fromtimestamp(float(since))
            and a['event'] == 'AVVIK']

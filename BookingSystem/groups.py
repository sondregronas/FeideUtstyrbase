import db


def get_all() -> list[str]:
    """Return a list of all groups in the database."""
    with db.connect() as (con, cur):
        cur.execute('SELECT classroom FROM groups ORDER BY classroom')
        groups = [row[0] for row in cur.fetchall()]

    return groups

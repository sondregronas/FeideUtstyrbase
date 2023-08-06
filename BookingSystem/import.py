"""
NOTE: Don't run this, unless you really need to (i.e. you've deleted the database and need to re-import all items).

This script imports all items from the label server into the database, if they don't already exist.

You shouldn't really need this script, but it's here just in case. Whenever you print a label, the label server
keeps track of it in its audit log. This script reads the audit log and imports all items into the database.
"""

import sqlite3

import requests

from __init__ import DATABASE, LABEL_SERVER


def get_items_from_label_server() -> list:
    """Get all items from the label server."""
    response = requests.get(f'{LABEL_SERVER}/audits')
    json = response.json()
    filtered = []
    for i in [{key: value.strip() for key, value in i.items()} for i in json]:
        if i['id'] not in [ii['id'] for ii in filtered]:
            filtered.append(item)
    return filtered


if __name__ == '__main__':
    with sqlite3.connect(DATABASE) as conn:
        cur = conn.cursor()
        for item in get_items_from_label_server():
            try:
                cur.execute("INSERT INTO inventory (id, name, category, last_seen) VALUES (?, ?, ?, ?)",
                            (item["id"], item["name"], item["category"], item["timestamp"]))
                print(f'Added item {item} to database.')
            except sqlite3.IntegrityError:
                print(f'Item {item} already exists in database.')
                continue
        conn.commit()

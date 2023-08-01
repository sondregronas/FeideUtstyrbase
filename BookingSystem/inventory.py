import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta

from __init__ import logger, DATABASE, audits
from db import read_sql_query

"""
Schema for items and functions to interact with the database.
"""


def all_categories() -> list[str]:
    """Get all categories."""
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    sql = 'SELECT * FROM categories'
    cur.execute(sql)
    categories = [row[1] for row in cur.fetchall()]
    con.close()
    return categories


# TODO: Use a context manager to open and close the database connection, instead of opening and closing it for every function


@dataclass
class Item:
    id: str
    name: str
    category: str
    included_batteries: int = 0
    available: int = 1
    active_order: str = None
    order_due_date: str = None
    last_seen: str = None

    def __str__(self) -> str:
        return f'{self.id}, {self.name}, {self.category}'


def add(item: Item) -> None:
    """Add the given item to the database."""
    con = sqlite3.connect(DATABASE)
    try:
        con.execute(read_sql_query('add_item.sql'), item.__dict__)
        con.commit()
        logger.info(f'Added item {item.id} to database.')
        logger.debug(f'Added item {item.id} to database with values {item.__dict__}')
    except sqlite3.IntegrityError:
        logger.error(f'Item {item.id} already exists in database.')
        raise ValueError(f'Item {item.id} already exists in database.')
    finally:
        con.close()
    _update_last_seen(item.id)
    audits.info(f'NEW - Added item {item.id} to database. ({item})')


def edit(old_item_id: str, new_item: Item) -> None:
    """Edit the item with the given ID in the database."""
    old = get(old_item_id)
    con = sqlite3.connect(DATABASE)
    try:
        SQL = 'UPDATE inventory SET id=:id, name=:name, category=:category, included_batteries=:included_batteries WHERE id=:old_item_id'
        con.execute(SQL, {**new_item.__dict__, 'old_item_id': old_item_id})
        con.commit()
        logger.info(f'Edited item {old_item_id} in database.')
        logger.debug(f'Edited item {old_item_id} in database with values {new_item.__dict__}')
    except sqlite3.IntegrityError:
        logger.error(f'Item {new_item.id} already exists in database.')
        raise ValueError(f'Item {new_item.id} already exists in database.')
    finally:
        con.close()
    _update_last_seen(new_item.id)
    diff = ', '.join([f'{old.__dict__[key]}->{new_item.__dict__[key]}' for key in old.__dict__
                      if old.__dict__[key] != new_item.__dict__[key]
                      and new_item.__dict__[key] is not None])
    audits.info(f'EDITED - Edited item {old_item_id} in database ({diff}).')


def delete(item_id: str) -> None:
    """Delete the item with the given ID from the database."""
    con = sqlite3.connect(DATABASE)
    try:
        SQL = 'DELETE FROM inventory WHERE id=:id'
        con.execute(SQL, {'id': item_id})
        con.commit()
        logger.info(f'Deleted item {item_id} from database.')
    except sqlite3.IntegrityError:
        logger.error(f'Item {item_id} does not exist in database.')
        raise ValueError(f'Item {item_id} does not exist in database.')
    finally:
        con.close()
    audits.info(f'REMOVED - Deleted item {item_id} from database.')


def get(item_id: str) -> Item:
    """Return a JSON object of the item with the given ID."""
    con = sqlite3.connect(DATABASE)
    item = Item(*con.execute(read_sql_query('get_item.sql'), {'id': item_id}).fetchone())
    con.close()
    return item


def get_all() -> list[Item]:
    """Return a JSON list of all items in the database."""
    con = sqlite3.connect(DATABASE)
    items = [Item(*row) for row in con.execute(read_sql_query('get_all_items.sql'))]
    con.close()
    return items


def get_all_overdue() -> list[Item]:
    """Return a JSON list of all overdue items in the database."""
    con = sqlite3.connect(DATABASE)
    items = [Item(*row) for row in con.execute(read_sql_query('get_all_overdue.sql'))]
    con.close()
    return items


def get_all_non_overdue() -> list[Item]:
    """Return a JSON list of all overdue items in the database."""
    con = sqlite3.connect(DATABASE)
    items = [Item(*row) for row in con.execute(read_sql_query('get_all_non_overdue.sql'))]
    con.close()
    return items


def _update_last_seen(item_id: str) -> None:
    """Update the last_seen column of the item with the given ID."""
    con = sqlite3.connect(DATABASE)
    try:
        SQL = 'UPDATE inventory SET last_seen=datetime("now") WHERE id=:id'
        con.execute(SQL, {'id': item_id})
        con.commit()
    except sqlite3.IntegrityError:
        print(f'Item {item_id} does not exist in database.')
    finally:
        con.close()


def register_out(item_id: str, user: str, days: str = 1) -> None:
    """Set the item with the given ID to unavailable and register the order details."""
    due_date = datetime.now() + timedelta(days=datetime.strptime(days, '%d').day)

    item = get(item_id)
    if item.available == 0:
        register_in(item_id)

    con = sqlite3.connect(DATABASE)
    try:
        sql = 'UPDATE inventory SET available=0, active_order=:active_order, order_due_date=:order_due_date WHERE id=:id'
        con.execute(sql, {'id': item_id, 'active_order': user, 'order_due_date': due_date})
        con.commit()
        logger.info(f'Item {item_id} is now unavailable.')
    except sqlite3.IntegrityError:
        logger.error(f'Item {item_id} does not exist in database.')
        raise ValueError(f'Item {item_id} does not exist in database.')
    finally:
        con.close()
    _update_last_seen(item_id)
    audits.info(f'OUT - Item {item_id} was registered out to {user} for {days} days.')


def register_in(item_id: str) -> None:
    """Set the item with the given ID to available and remove the order details."""
    try:
        get(item_id)
    except TypeError:
        raise ValueError(f'Item {item_id} does not exist in database.')

    con = sqlite3.connect(DATABASE)
    try:
        sql = 'UPDATE inventory SET available=1, active_order=NULL, order_due_date=NULL WHERE id=:id'
        con.execute(sql, {'id': item_id})
        con.commit()
        logger.info(f'Item {item_id} is now available.')
    except sqlite3.IntegrityError:
        logger.error(f'Item {item_id} does not exist in database.')
        raise ValueError(f'Item {item_id} does not exist in database.')
    finally:
        con.close()
    _update_last_seen(item_id)
    audits.info(f'IN - Item {item_id} is now available.')

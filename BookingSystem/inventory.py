import sqlite3
from dataclasses import dataclass

from __init__ import logger, DATABASE
from db import read_sql_query

"""
Schema for items and functions to interact with the database.
"""

# TODO: Have this be adjustable from frontend
categories = [
    'Kamera',
    'Objektiv',
    'Batteri',
    'Lader',
    'Strømforsyning',
    'Minnekort',
    'Minnekortleser',
    'Lys',
    'Mikrofon',
    'Stativ',
    'Filter',
    'Lydopptaker',
    'Adapter',
    'Skjerm',
    'Gimbal',
    'Drone',
    'Tegnebrett',
    'Lagringsenhet',
    'Headset',
    'Kabel',
    'Diverse',
    'Mangler kategori',
]


@dataclass
class Item:
    id: str
    name: str
    category: str
    included_batteries: int = 0
    available: int = 1
    active_order: str = None
    order_due_date: str = None

    def __str__(self) -> str:
        return f'{self.id} | {self.name} | {self.category} | {self.included_batteries}'


def add(item: Item) -> None:
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


def edit(old_item_id: str, new_item: Item) -> None:
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


def delete(item_id: str) -> None:
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


def get(item_id: str) -> Item:
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

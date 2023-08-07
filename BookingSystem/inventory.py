import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta

from dateutil import parser

import audits
import user
from __init__ import logger, DATABASE
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
    borrowed_to: str = None
    order_due_date: str = None
    last_seen: str = None

    def api_repr(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'available': self.available,
            'borrowed_to': self.borrowed_to,
            'order_due_date': self.order_due_date,
            'last_seen': self.last_seen
        }

    def __str__(self) -> str:
        if self.order_due_date:
            return f'{self.lender_name}: {self.id} - {self.name} ({self.category}, {parser.parse(self.order_due_date):%d.%m.%Y})'
        return f'{self.id} - {self.name} - {self.category}'

    @property
    def user(self) -> dict:
        if self.borrowed_to is None:
            return {}
        return user.get(self.borrowed_to)

    @property
    def lender_name(self) -> str:
        if not self.user.get('name'):
            return 'Slettet bruker'
        return self.user.get('name')

    @property
    def lender_association(self) -> str:
        if not self.user.get('name'):
            return 'Se logg'
        return self.user.get('classroom') or 'Lærer'

    @property
    def lender(self) -> str:
        return f'{self.lender_name} ({self.lender_association})'

    @property
    def overdue(self) -> bool:
        if self.order_due_date is None:
            return False
        return parser.parse(self.order_due_date) < datetime.now()


def add(item: Item) -> None:
    """Add the given item to the database."""
    con = sqlite3.connect(DATABASE)
    try:
        con.execute(read_sql_query('add_item.sql'), item.__dict__)
        con.commit()
        logger.info(f'La til {item.id} i databasen.')
        logger.debug(f'La til {item.id} i databasen med verdiene {item.__dict__}')
    except sqlite3.IntegrityError:
        logger.error(f'{item.id} finnes i databasen fra før.')
        raise ValueError(f'{item.id} finnes i databasen fra før.')
    finally:
        con.close()
    _update_last_seen(item.id)
    audits.audit('ITEM_NEW', f'{item.id} ble lagt til i databasen. ({item})')


def edit(old_item_id: str, new_item: Item) -> None:
    """Edit the item with the given ID in the database."""
    old = get(old_item_id)
    con = sqlite3.connect(DATABASE)
    try:
        sql = 'UPDATE inventory SET id=:id, name=:name, category=:category, included_batteries=:included_batteries WHERE id=:old_item_id'
        con.execute(sql, {**new_item.__dict__, 'old_item_id': old_item_id})
        con.commit()
        logger.info(f'Redigerte utstyr {old_item_id} i databasen.')
        logger.debug(f'Redigerte utstyr {old_item_id} i databasen med verdiene {new_item.__dict__}')
    except sqlite3.IntegrityError:
        logger.error(f'{new_item.id} eksisterer allerede i databasen.')
        raise ValueError(f'{new_item.id} eksisterer allerede i databasen.')
    finally:
        con.close()
    _update_last_seen(new_item.id)
    diff = ', '.join([f'{old.__dict__[key]}->{new_item.__dict__[key]}' for key in old.__dict__
                      if old.__dict__[key] != new_item.__dict__[key]
                      and new_item.__dict__[key] is not None])
    # TODO: Fix this
    if diff == '0->0':
        return
    audits.audit('ITEM_EDIT', f'{old_item_id} ble redigert i databasen ({diff}).')


def delete(item_id: str) -> None:
    """Delete the item with the given ID from the database."""
    con = sqlite3.connect(DATABASE)
    try:
        sql = 'DELETE FROM inventory WHERE id=:id'
        con.execute(sql, {'id': item_id})
        con.commit()
        logger.info(f'Slettet utstyr {item_id} fra databasen.')
    except sqlite3.IntegrityError:
        logger.error(f'{item_id} eksisterer ikke i databasen.')
        raise ValueError(f'{item_id} eksisterer ikke i databasen.')
    finally:
        con.close()
    audits.audit('ITEM_REM', f'{item_id} ble slettet fra databasen.')


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


def get_all_available() -> list[Item]:
    """Return a JSON list of all available items in the database."""
    con = sqlite3.connect(DATABASE)
    items = [Item(*row) for row in con.execute('SELECT * FROM inventory WHERE available=1')]
    con.close()
    return items


def get_all_unavailable() -> list[Item]:
    """Return a JSON list of all unavailable items in the database."""
    con = sqlite3.connect(DATABASE)
    items = [Item(*row) for row in con.execute('SELECT * FROM inventory WHERE available=0')]
    con.close()
    return items


def get_all_overdue() -> list[Item]:
    """Return a JSON list of all overdue items in the database."""
    con = sqlite3.connect(DATABASE)
    items = [Item(*row) for row in con.execute(read_sql_query('get_all_overdue.sql'))]
    con.close()
    return items


def _update_last_seen(item_id: str) -> None:
    """Update the last_seen column of the item with the given ID."""
    con = sqlite3.connect(DATABASE)
    try:
        sql = "UPDATE inventory SET last_seen=DATETIME('now','localtime') WHERE id=:id"
        con.execute(sql, {'id': item_id})
        con.commit()
    except sqlite3.IntegrityError:
        print(f'{item_id} eksisterer ikke i databasen.')
    finally:
        con.close()


def register_out(item_id: str, userid: str, days: str = 1) -> None:
    """Set the item with the given ID to unavailable and register the order details."""
    due_date = datetime.now() + timedelta(days=datetime.strptime(days, '%d').day)

    item = get(item_id)
    if item.available == 0:
        register_in(item_id)

    con = sqlite3.connect(DATABASE)
    try:
        sql = 'UPDATE inventory SET available=0, borrowed_to=:borrowed_to, order_due_date=:order_due_date WHERE id=:id'
        con.execute(sql, {'id': item_id, 'borrowed_to': userid, 'order_due_date': due_date})
        con.commit()
        logger.info(f'{item_id} er ikke lenger tilgjengelig.')
    except sqlite3.IntegrityError:
        logger.error(f'{item_id} eksisterer ikke i databasen.')
        raise ValueError(f'{item_id} eksisterer ikke i databasen.')
    finally:
        con.close()
    _update_last_seen(item_id)
    u = user.get(userid)
    audits.audit('REG_OUT',
                 f'{item_id} ble registrert ut til {u.get("name")} ({u.get("classroom") or "Lærer"}) i {days} dager.')


def register_in(item_id: str) -> None:
    """Set the item with the given ID to available and remove the order details."""
    try:
        get(item_id)
    except TypeError:
        raise ValueError(f'{item_id} eksisterer ikke i databasen.')

    con = sqlite3.connect(DATABASE)
    try:
        sql = 'UPDATE inventory SET available=1, borrowed_to=NULL, order_due_date=NULL WHERE id=:id'
        con.execute(sql, {'id': item_id})
        con.commit()
        logger.info(f'{item_id} er nå tilgjengelig.')
    except sqlite3.IntegrityError:
        logger.error(f'{item_id} eksisterer ikke i databasen.')
        raise ValueError(f'{item_id} eksisterer ikke i databasen.')
    finally:
        con.close()
    _update_last_seen(item_id)
    audits.audit('REG_IN', f'{item_id} er nå tilgjengelig.')

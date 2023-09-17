from dataclasses import dataclass
from datetime import datetime

from flask import request

import db
from __init__ import KIOSK_FQDN, logger
from db import read_sql_query
from feide import get_feide_data


# TODO: Fix User class, right now it serves as both a database model and a session model,
#       except it doesn't really work as either.
@dataclass
class User:
    name: str
    email: str
    userid: str
    affiliations: list[str] = list

    def update(self) -> None:
        """Update the user's information from login provider. (OAuth)"""
        ...

    @property
    def is_admin(self) -> bool:
        """Check if the user is an admin."""
        admin_affiliations = ['employee', 'staff', 'admin']
        return any(x in self.affiliations for x in admin_affiliations)

    @property
    def exists(self) -> bool:
        """Check if the user exists in the database."""
        return bool(get(self.userid))

    @property
    def classroom(self) -> str:
        """Get the classroom the user is associated with."""
        return get(self.userid).get('classroom', '')

    @property
    def active(self) -> bool:
        """Check if the user is active."""
        if get(self.userid).get('admin'):
            return True
        date_from_string = datetime.fromisoformat(get(self.userid).get('expires_at', '1970-01-01'))
        return date_from_string > datetime.now()


class FeideUser(User):  # pragma: no cover
    def update(self) -> None:
        """Get the latest information from Feide, ensuring it is up-to-date and is a valid user."""
        data = get_feide_data()
        self.name = data['name']
        self.email = data['email']
        self.userid = data['userid']
        self.affiliations = data['affiliations']


class KioskUser(User):
    @property
    def is_admin(self) -> bool:
        return request.headers.get('Host') == KIOSK_FQDN


def separate_classroom_teacher(classroom: str) -> tuple[str, str]:
    """Separate the classroom and teacher from a string."""
    if not classroom:
        return '', ''
    if '(' in classroom:
        return classroom.split('(')[0].strip(), classroom.split('(')[1].strip(')')
    return classroom, ''


def get_all_active_users() -> list[dict]:
    """Return a list of all active users in the database."""
    with db.connect() as (con, cur):
        cur.execute(read_sql_query('get_all_active_users.sql'))
        columns = [description[0] for description in cur.description]
        data = [{columns[i]: user[i] for i in range(len(columns))} for user in cur.fetchall()]

    for user in data:
        user['classroom'], user['teacher'] = separate_classroom_teacher(user['classroom'])
    return data


def prune_inactive() -> None:
    """Remove all inactive users from the database."""
    with db.connect() as (con, cur):
        cur.execute(read_sql_query('prune_inactive_users.sql'))


def get(userid: str) -> dict:
    """Load the user's information from the database."""
    with db.connect() as (con, cur):
        cur.execute(read_sql_query("get_user_by_id.sql"), (userid,))
        user = cur.fetchone()
        columns = [description[0] for description in cur.description]

    if not user:
        return {}
    return {columns[i]: user[i] for i in range(len(columns)) if not columns[i] == 'id'}


def delete(userid: str) -> None:
    """Delete the user from the database."""
    with db.connect() as (con, cur):
        cur.execute('DELETE FROM users WHERE userid = ?', (userid,))
    logger.debug(f'Deleted user {userid}')

import sqlite3
from dataclasses import dataclass
from datetime import datetime

from flask import request

from __init__ import DATABASE, KIOSK_FQDN
from db import get_user, read_sql_query
from feide import get_feide_data


# TODO: Fix User class, right now it serves as both a database model and a session model,
#       except it doesn't really work as either.
@dataclass
class User:
    name: str
    email: str
    userid: str
    affiliations: list[str]

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
        return bool(get_user(self.userid))

    @property
    def classroom(self) -> str:
        """Get the classroom the user is associated with."""
        return get_user(self.userid).get('classroom')

    @property
    def active(self) -> bool:
        """Check if the user is active."""
        if get_user(self.userid).get('admin'):
            return True
        date_from_string = datetime.fromisoformat(get_user(self.userid).get('expires_at', '1970-01-01'))
        return date_from_string > datetime.now()


class FeideUser(User):
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


def get_all_active_users() -> list[dict]:
    """Return a list of all active users in the database."""
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute(read_sql_query('get_all_active_users.sql'))
    columns = [description[0] for description in cur.description]
    data = [{columns[i]: user[i] for i in range(len(columns))} for user in cur.fetchall()]
    con.close()
    return data


def prune_inactive() -> None:
    """Remove all inactive users from the database."""
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute(read_sql_query('prune_old_users.sql'))
    con.commit()
    con.close()

from dataclasses import dataclass
from datetime import datetime

from db import get_user
from feide import get_feide_data


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
        date_from_string = datetime.fromisoformat(get_user(self.userid).get('expires_at'))
        return date_from_string > datetime.now()


class FeideUser(User):
    def update(self) -> None:
        """Get the latest information from Feide, ensuring it is up-to-date and is a valid user."""
        data = get_feide_data()
        self.name = data['name']
        self.email = data['email']
        self.userid = data['userid']
        self.affiliations = data['affiliations']

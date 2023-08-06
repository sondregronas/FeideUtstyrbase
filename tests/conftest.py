import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parent.parent) + '\\BookingSystem')
import BookingSystem.app as app
from BookingSystem.db import init_db
from BookingSystem.user import User


class AdminUser(User):
    def __init__(self):
        self.name = 'Admin User'
        self.email = 'admin@test'
        self.userid = 'admin-userid'
        self.affiliations = ['admin']

    @property
    def is_admin(self) -> bool:
        return True


class StudentUser(User):
    def __init__(self):
        self.name = 'Student User'
        self.email = 'student@test'
        self.userid = 'student-userid'
        self.affiliations = ['student']

    @property
    def is_admin(self) -> bool:
        return False


@pytest.fixture
def client():
    flask_app = app.create_app()
    flask_app.config['TESTING'] = True
    init_db()
    yield flask_app.test_client()

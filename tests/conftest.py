import sys
from pathlib import Path

import flask
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
    def __init__(self,
                 userid: str = 'student-userid',
                 name: str = 'Student User',
                 email: str = 'student@test'):
        self.name = name
        self.email = email
        self.userid = userid
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


@pytest.fixture
def admin_client(client):
    with client.session_transaction() as session:
        session['user'] = AdminUser()
    yield client


@pytest.fixture
def student_client(client):
    with client.session_transaction() as session:
        session['user'] = StudentUser()
    yield client


def url_for(client, endpoint: str, **kwargs) -> str:
    """
    Helper function to get url for endpoint.
    """
    fns = client.application.view_functions

    for fn in fns:
        if fn != endpoint:
            continue
        context = client.application.test_request_context()
        context.push()
        url = flask.url_for(fn, **kwargs)
        context.pop()
        return url

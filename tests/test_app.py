import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parent.parent) + '\\BookingSystem')
import BookingSystem.app as app
from BookingSystem.db import init_db


@pytest.fixture
def client():
    flask_app = app.create_app()
    flask_app.config['TESTING'] = True
    init_db()
    yield flask_app.test_client()


def test_index_unauthorized(client):
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_login(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert '/login/feide' in response.data.decode('utf-8')

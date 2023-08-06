import pytest  # noqa: F401

from conftest import *


def test_index(client):
    """
    Should redirect to /login if not logged in
    /admin should be visible if logged in as admin
    /admin should not be visible if logged in as student
    """
    # Not logged in
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' == response.headers['Location']

    # Logged in as admin
    with client.session_transaction() as session:
        session['user'] = AdminUser()
    response = client.get('/')
    assert response.status_code == 200
    assert '/admin' in response.data.decode('utf-8')

    # Logged in as student
    with client.session_transaction() as session:
        session['user'] = StudentUser()
    response = client.get('/')
    assert response.status_code == 200
    assert '/admin' not in response.data.decode('utf-8')


def test_login(client):
    """
    Should redirect to / if already logged in
    """
    # Not logged in
    response = client.get('/login')
    assert response.status_code == 200
    assert '/login/feide' in response.data.decode('utf-8')

    # Logged in as admin
    with client.session_transaction() as session:
        session['user'] = AdminUser()
    response = client.get('/login')
    assert response.status_code == 302
    assert '/' == response.headers['Location']

    # Logged in as student
    with client.session_transaction() as session:
        session['user'] = StudentUser()
    response = client.get('/login')
    assert response.status_code == 302
    assert '/' == response.headers['Location']


def test_admin_page(client):
    """
    Should clear session cookie and send to /login if not admin
    """
    # Not logged in
    response = client.get('/admin')
    assert response.status_code == 302
    assert '/login' == response.headers['Location']

    # Logged in as admin
    with client.session_transaction() as session:
        session['user'] = AdminUser()
    response = client.get('/admin')
    assert response.status_code == 200

    # Logged in as student
    with client.session_transaction() as session:
        session['user'] = StudentUser()
    response = client.get('/admin')
    # Should clear session cookie if not admin
    # (could return a 403 instead, but this is simpler)
    with client.session_transaction() as session:
        assert 'user' not in session
    assert response.status_code == 302
    assert '/login' == response.headers['Location']


def test_logout(client):
    """
    Should redirect to /login and clear session cookie
    """
    # Not logged in
    response = client.get('/logout')
    assert response.status_code == 302
    assert '/login' == response.headers['Location']

    # Logged in as admin
    with client.session_transaction() as session:
        session['user'] = AdminUser()
    response = client.get('/logout')
    with client.session_transaction() as session:
        assert 'user' not in session
    assert response.status_code == 302
    assert '/login' == response.headers['Location']

    # Logged in as student
    with client.session_transaction() as session:
        session['user'] = StudentUser()
    response = client.get('/logout')
    with client.session_transaction() as session:
        assert 'user' not in session
    assert response.status_code == 302
    assert '/login' == response.headers['Location']

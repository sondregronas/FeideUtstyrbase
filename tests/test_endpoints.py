import flask
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


def test_template_errors_all_endpoints_without_args(client):
    """
    Test every endpoint that does not take arguments for errors.

    This test is probably a bad indicator of whether the app is working or not,
    but at least it will catch errors in the endpoints (such as missing templates or links)
    """

    for endpoint in client.application.view_functions:
        if endpoint.startswith('static'):
            continue

        # Skip endpoints with arguments
        args = client.application.view_functions[endpoint].__code__.co_varnames
        if args:
            continue

        context = client.application.test_request_context()
        context.push()
        url = flask.url_for(endpoint)
        context.pop()

        # Logged in as admin
        with client.session_transaction() as session:
            session['user'] = AdminUser()

        response = client.get(url)
        assert response.data


def test_public_endpoints(client):
    """
    Test every endpoint that does not have the login_required decorator.
    """

    expected_endpoints = [
        'app.login',
        'app.logout',
        'app.privacy',
        'app.responsibility',
        'feide.login',
        'feide.callback',
        'robots',
    ]

    for endpoint in client.application.view_functions:
        if endpoint.startswith('static'):
            continue

        func = client.application.view_functions[endpoint]
        login_required = getattr(func, 'login_required', False)
        if login_required:
            continue

        assert endpoint in expected_endpoints


def test_user_endpoints(client):
    """
    Test every endpoint that has the login_required decorator,
    but with admin_required or api_allowed set to False.
    """

    expected_endpoints = [
        'app.index',
        'app.login',
        'app.logout',
        'app.privacy',
        'app.responsibility',
        'app.register',
        'feide.login',
        'feide.callback',
        'api.register_student',
        'api.delete_me',
        'robots',
    ]

    for endpoint in client.application.view_functions:
        if endpoint.startswith('static'):
            continue

        func = client.application.view_functions[endpoint]
        admin_required = getattr(func, 'admin_required', False)
        api_access = getattr(func, 'api_access', False)
        if admin_required or api_access:
            continue

        assert endpoint in expected_endpoints


def test_api_endpoints(client):
    """
    Test every endpoint that has the login_required decorator,
    and with api_allowed set to True.
    """

    expected_endpoints = [
        'api.get_items',
        'api.get_items_available',
        'api.get_items_unavailable',
        'api.get_items_overdue',
        'api.get_items_by_userid',
        'api.get_user',
        'api.send_report',
        'api.prune_inactive_users',
        'api.backup',
    ]

    for endpoint in client.application.view_functions:
        if endpoint.startswith('static'):
            continue

        func = client.application.view_functions[endpoint]
        api_access = getattr(func, 'api_allowed', False)
        if not api_access:
            continue

        assert endpoint in expected_endpoints

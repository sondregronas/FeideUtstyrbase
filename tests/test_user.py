import db
import groups
from conftest import *


def add_classroom(client):
    """Helper function to add a classroom."""
    classroom = {'groups': 'Classroom (Teacher Name)\nClassroom2 (Teacher2 Name2)\n'}

    with client.session_transaction() as session:
        session['user'] = AdminUser()
    r = client.put(url_for(client, 'api.update_groups'), data=classroom, follow_redirects=True)
    assert r.status_code == 200
    assert groups.get_all() == ['Classroom (Teacher Name)', 'Classroom2 (Teacher2 Name2)']


def test_register_invalid(student_client):
    add_classroom(student_client)

    # Invalid classroom
    r = student_client.post(url_for(student_client, 'api.register_student'),
                            data={'classroom': 'h4x0r'})
    assert 'dQw4w9WgXcQ' in r.data.decode('utf-8')

    # Invalid teacher
    r = student_client.post(url_for(student_client, 'api.register_student'),
                            data={'h4x0r': 'Classroom (Teacher Name)'})
    assert 'dQw4w9WgXcQ' in r.data.decode('utf-8')


def test_register(client):
    # Set up the database to allow registration
    add_classroom(client)
    with client.session_transaction() as session:
        session['user'] = StudentUser()
        user = session['user']

    # Verify that the user is not registered
    r = client.get(url_for(client, 'app.index'))
    assert "Status: Du er klar" not in r.data.decode('utf-8')

    # Register
    client.post(url_for(client, 'api.register_student'),
                data={'classroom': 'Classroom (Teacher Name)'})

    # Verify that the user is now registered
    r = client.get(url_for(client, 'app.index'))
    assert "Status: Du er klar" in r.data.decode('utf-8')

    # Verify that the user is registered in the database
    with client.session_transaction() as session:
        session['user'] = AdminUser()
    r = client.get(url_for(client, 'api.get_user', userid=user.userid))
    assert r.status_code == 200
    assert r.json['name'] == user.name
    assert not r.json['admin']
    assert r.json['classroom'] == 'Classroom (Teacher Name)'

    # Register again using a different classroom
    with client.session_transaction() as session:
        session['user'] = StudentUser()
    client.post(url_for(client, 'api.register_student'),
                data={'classroom': 'Classroom2 (Teacher2 Name2)'})
    with client.session_transaction() as session:
        session['user'] = AdminUser()

    # Verify that the updated classroom is registered in the database
    r = client.get(url_for(client, 'api.get_user', userid=user.userid))
    assert r.status_code == 200
    assert r.json['classroom'] == 'Classroom2 (Teacher2 Name2)'


def test_delete_user(client):
    # Set up the database to allow registration
    add_classroom(client)
    with client.session_transaction() as session:
        session['user'] = StudentUser()
        user = session['user']

    # Register
    client.post(url_for(client, 'api.register_student'),
                data={'classroom': 'Classroom (Teacher Name)'})

    # Log in as admin
    with client.session_transaction() as session:
        session['user'] = AdminUser()

    # Verify that the user is registered
    r = client.get(url_for(client, 'api.get_user', userid=user.userid))
    assert r.status_code == 200
    assert r.json['name'] == user.name
    assert r.json

    with client.session_transaction() as session:
        # Log in as the user
        session['user'] = StudentUser()
        # Verify that the user is logged in
        assert 'user' in session

    # Delete the user (current user)
    r = client.delete(url_for(client, 'api.delete_me', userid=user.userid))
    assert r.status_code == 200

    with client.session_transaction() as session:
        # Verify that the user is logged out
        assert 'user' not in session
        # Log in as admin
        session['user'] = AdminUser()

    # Verify that the user is deleted
    r = client.get(url_for(client, 'api.get_user', userid=user.userid))
    assert not r.json


def test_register_admin(client):
    """Verify that admins cannot register."""
    with client.session_transaction() as session:
        session['user'] = AdminUser()
        user = session['user']

    r = client.get(url_for(client, 'api.get_user', userid=user.userid))
    assert not r.json

    # Register
    r = client.get(url_for(client, 'app.register'), follow_redirects=True)
    assert r.status_code == 200

    r = client.get(url_for(client, 'api.get_user', userid=user.userid))
    assert r.json
    assert r.json['admin']

    # Delete the user (current user)
    client.delete(url_for(client, 'api.delete_me', userid=user.userid))


def test_prune_inactive(admin_client):
    from test_booking import ctx_booking
    with ctx_booking(admin_client, 1, 0) as ctx:
        r = admin_client.get(url_for(admin_client, 'api.get_user', userid=ctx.users[0].userid)).json
        assert r['name'] == ctx.users[0].name
        assert r['userid'] == ctx.users[0].userid

        r = admin_client.post(url_for(admin_client, 'api.prune_inactive_users'))
        assert r.status_code == 200

        r = admin_client.get(url_for(admin_client, 'api.get_user', userid=ctx.users[0].userid)).json
        assert r['name'] == ctx.users[0].name
        assert r['userid'] == ctx.users[0].userid

        with db.connect() as (con, cur):
            # update expires_at in users where userid = ctx.users[0].userid
            cur.execute(
                f"""UPDATE users SET expires_at = DATETIME('now', '-365 days') WHERE userid = '{ctx.users[0].userid}'""")

        r = admin_client.post(url_for(admin_client, 'api.prune_inactive_users'))
        assert r.status_code == 200

        r = admin_client.get(url_for(admin_client, 'api.get_user', userid=ctx.users[0].userid)).json
        assert not r

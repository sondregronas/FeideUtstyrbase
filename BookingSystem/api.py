"""
Routes to interact with the database. (API endpoints.)

This should be called from the frontend to get data from the database.
Filtering and sorting should be done on the frontend, not the backend.
"""
import sqlite3
from datetime import datetime

import flask

from BookingSystem import inventory, DATABASE, groups
from BookingSystem.utils import login_required, next_july

api = flask.Blueprint('api', __name__)


@api.route('/items', methods=['GET'])
@login_required(admin_only=True)
def get_items() -> flask.Response:
    """Get all items in the database for frontend display."""
    items = inventory.get_all()
    return flask.jsonify([item for item in items])


@api.route('/items/<item_id>', methods=['GET'])
@login_required(admin_only=True)
def get_item(item_id: str) -> flask.Response:
    """Get a single item from the database."""
    item = inventory.get(item_id)
    return flask.jsonify(item)


@api.route('/groups', methods=['GET'])
@login_required(admin_only=True)
def get_groups() -> flask.Response:
    """Get all groups in the database for frontend display."""
    return flask.jsonify([group.strip() for group in groups.get_all()])


@api.route('/users', methods=['GET'])
@login_required(admin_only=True)
def get_users() -> flask.Response:
    """Get all users in the database for frontend display."""
    # TODO: Only return valid users
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute('SELECT * FROM users')
    columns = [description[0] for description in cur.description]
    data = [{columns[i]: user[i] for i in range(len(columns))} for user in cur.fetchall()]
    con.close()
    return flask.jsonify(data)


@api.route('/update/student', methods=['POST'], endpoint='update_student')
@login_required()
def update_student() -> flask.Response:
    """Update a class in the database."""
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    data = {
        'name': flask.session.get('user').name,
        'email': flask.session.get('user').email,
        'userid': flask.session.get('user').userid,
        'classroom': flask.request.form.get('classroom'),
        'updated_at': datetime.now().isoformat(),
        'expires_at': next_july().isoformat()
    }
    cur.execute(
        'REPLACE INTO users (name, email, userid, classroom, updated_at, expires_at) '
        'VALUES (:name, :email, :userid, :classroom, :updated_at, :expires_at)',
        data)
    con.commit()
    con.close()
    return flask.redirect(flask.request.referrer)


@api.route('/update/groups', methods=['POST'], endpoint='update_groups')
@login_required(admin_only=True)
def update_groups() -> flask.Response:
    """Update a class in the database."""
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute('DELETE FROM groups')
    con.commit()

    for group in flask.request.form.get('groups').split('\n'):
        if not group.strip():
            continue
        cur.execute('INSERT INTO groups (classroom) VALUES (?)', (group,))
    con.commit()
    con.close()
    return flask.redirect(flask.request.referrer)

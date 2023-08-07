"""
Routes to interact with the database. (API endpoints.)

This should be called from the frontend to get data from the database.
Filtering and sorting should be done on the frontend, not the backend.
"""
import sqlite3
from datetime import datetime

import flask
import requests

import inventory
import mail
import user
from __init__ import DATABASE, LABEL_SERVER
from inventory import Item
from utils import login_required, next_july

api = flask.Blueprint('api', __name__)


@api.route('/items', methods=['GET'])
@login_required(admin_only=True, api=True)
def get_items() -> flask.Response:
    """Get all items in the database for frontend display."""
    items = inventory.get_all()
    return flask.jsonify([item.api_repr() for item in items])


@api.route('/items/available', methods=['GET'])
@login_required(admin_only=True, api=True)
def get_items_available() -> flask.Response:
    """Get all items in the database for frontend display."""
    items = inventory.get_all_available()
    return flask.jsonify([item.api_repr() for item in items])


@api.route('/items/unavailable', methods=['GET'])
@login_required(admin_only=True, api=True)
def get_items_unavailable() -> flask.Response:
    """Get all items in the database for frontend display."""
    items = inventory.get_all_unavailable()
    return flask.jsonify([item.api_repr() for item in items])


@api.route('/items/overdue', methods=['GET'])
@login_required(admin_only=True, api=True)
def get_items_overdue() -> flask.Response:
    """Get all items in the database for frontend display."""
    items = inventory.get_all_overdue()
    return flask.jsonify([item.api_repr() for item in items])


@api.route('/items/user/<userid>', methods=['GET'])
@login_required(admin_only=True, api=True)
def get_items_by_userid(userid: str) -> flask.Response:
    items = inventory.get_all_unavailable()
    return flask.jsonify([item.api_repr() for item in items if item.borrowed_to == userid])


@api.route('/items/add', methods=['POST'])
@login_required(admin_only=True)
def add_item() -> flask.Response:
    """Add an item to the database."""
    form = flask.request.form
    item = {key: form.get(key) for key in form.keys() if key in Item.__annotations__}
    item = Item(**item)
    print_label_count = int(form.get('print_label_count'))
    print_label_type = form.get('print_label_type')
    try:
        inventory.add(item)
    except ValueError as e:
        return flask.Response(str(e), status=400)
    if print_label_count > 0:
        url = f'{LABEL_SERVER}/print?count={print_label_count}&variant={print_label_type}&id={item.id}&name={item.name}&category={item.category}'
        print(url)
    return flask.Response(f'La til {item.id} i databasen.', status=201)


@api.route('/items/edit/<item_id>', methods=['POST'])
@login_required(admin_only=True)
def edit_item(item_id: str) -> flask.Response:
    """Edit an item in the database."""
    form = flask.request.form
    item = {key: form.get(key) for key in form.keys() if key in Item.__annotations__}
    item = Item(**item)

    try:
        inventory.edit(item_id, item)
    except ValueError as e:
        return flask.Response(str(e), status=400)
    return flask.Response(f'Redigerte {item_id} i databasen.', status=200)


@api.route('/items/delete/<item_id>', methods=['POST'])
@login_required(admin_only=True)
def delete_item(item_id: str) -> flask.Response:
    """Delete an item from the database."""
    try:
        inventory.delete(item_id)
    except ValueError as e:
        return flask.Response(str(e), status=400)
    return flask.Response(f'Slettet {item_id} fra databasen.', status=200)


@api.route('/items/<item_id>/label/<variant>/preview', methods=['GET'])
@login_required(admin_only=True)
def get_label_preview(item_id: str, variant: str = 'qr') -> flask.Response:
    """Get a label preview for an item."""
    item = inventory.get(item_id)
    url = f'{LABEL_SERVER}/preview?id={item.id}&name={item.name}&variant={variant}'
    return flask.redirect(url)


@api.route('/items/<item_id>/label/print', methods=['POST'])
@login_required(admin_only=True)
def print_label(item_id: str) -> flask.Response:
    form = flask.request.form
    variant = form.get('print_label_type', 'qr')
    count = int(form.get('print_label_count', '1'))
    item = inventory.get(item_id)
    url = f'{LABEL_SERVER}/print?id={item.id}&name={item.name}&variant={variant}&count={count}'
    try:
        response = requests.post(url)
    except Exception as e:
        return flask.Response(str(e), status=500)
    return flask.Response(response.text, status=response.status_code)


@api.route('/book/out', methods=['POST'])
@login_required(admin_only=True)
def book_equipment() -> flask.Response:
    """Book out equipment for a user."""
    form = flask.request.form
    userid = form.get('user')
    days = form.get('days')
    item_ids = form.getlist('equipment')

    for item in item_ids:
        inventory.register_out(item_id=item, userid=userid, days=days)
    return flask.Response(f'Utstyret ble utlevert til {user.get(userid).get("name")}.', status=200)


@api.route('/return/<item_id>', methods=['POST'])
@login_required(admin_only=True)
def return_equipment(item_id: str) -> flask.Response:
    """Return equipment from a user."""
    try:
        inventory.register_in(item_id=item_id)
    except ValueError as e:
        return flask.Response(str(e), status=400)
    return flask.Response('Utstyr ble innlevert.', status=200)


@api.route('/user/<userid>', methods=['GET'])
@login_required(admin_only=True, api=True)
def get_user(userid: str) -> flask.Response:
    """Get user as JSON."""
    u = user.get(userid)
    if not u:
        return flask.abort(404)
    return flask.jsonify(u)


@api.route('/update/student', methods=['POST'], endpoint='update_student')
@login_required(admin_only=True)
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
    # noinspection SqlWithoutWhere
    cur.execute('DELETE FROM groups')
    con.commit()

    for group in flask.request.form.get('groups').split('\n'):
        if not group.strip():
            continue
        cur.execute('INSERT INTO groups (classroom) VALUES (?)', (group.strip(),))

    con.commit()
    con.close()
    return flask.redirect(flask.request.referrer)


@api.route('/update/categories', methods=['POST'], endpoint='update_categories')
@login_required(admin_only=True)
def update_categories() -> flask.Response:
    """Update every category in the database."""
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    # noinspection SqlWithoutWhere
    cur.execute('DELETE FROM categories')
    con.commit()

    for category in flask.request.form.get('categories').split('\n'):
        if not category.strip():
            continue
        cur.execute('INSERT INTO categories (name) VALUES (?)', (category.strip(),))

    con.commit()
    con.close()
    return flask.redirect(flask.request.referrer)


@api.route('/update/emails', methods=['POST'], endpoint='update_emails')
@login_required(admin_only=True)
def update_emails() -> flask.Response:
    """Update every email in the database."""
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    # noinspection SqlWithoutWhere
    cur.execute('DELETE FROM emails')
    con.commit()

    for email in flask.request.form.get('emails').split('\n'):
        if not email.strip():
            continue
        cur.execute('INSERT INTO emails (email) VALUES (?)', (email.strip(),))

    con.commit()
    con.close()
    return flask.redirect(flask.request.referrer)


@api.route('/email/report', methods=['POST'], endpoint='email_report')
@login_required(admin_only=True, api=True)
def email_report() -> flask.Response:
    """Emails a report to all users in the emails table.

    Can be used with a cron job to send reports automatically, e.g.:
    15 8 * 1-6,8-12 MON curl -X POST "http://localhost:5000/email/report?interval=7&token=<token>"

    If the interval parameter is set, the report will only be sent
    if the last report was sent more than interval days ago.
    """
    interval = flask.request.args.get('interval')
    if interval:
        last_sent = datetime.fromtimestamp(float(mail.get_last_sent())).date()
        current_date = datetime.now().date()
        if last_sent and (current_date - last_sent).days < int(interval):
            return flask.Response(f'Ikke sendt - mindre enn {interval} dager siden forrige rapport.', status=200)
    return mail.send_report()


@api.route('/users/prune_inactive', methods=['POST'], endpoint='prune_inactive_users')
@login_required(admin_only=True, api=True)
def prune_inactive_users() -> flask.Response:
    """Prune users that have not been updated in a while.

    Example cronjob:
    0 1 1 7 * curl -X POST "http://localhost:5000/users/prune_inactive?token=<token>"
    """
    user.prune_inactive()
    return flask.Response('Inaktive brukere ble fjernet.', status=200)


@api.route('/delete/me', methods=['POST'])
@login_required()
def delete_me() -> flask.Response:
    """Delete the currently logged in user."""
    u = flask.session.get("user")
    user.delete(u.userid)
    flask.session.clear()
    return flask.redirect(flask.url_for('app.login'))

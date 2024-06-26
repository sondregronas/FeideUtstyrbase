"""
Routes to interact with the database. (API endpoints.)

This should be called from the frontend to get data from the database.
Filtering and sorting should be done on the frontend, not the backend.
"""
from datetime import datetime

import flask
import markupsafe
import requests

import audits
import db
import inventory
import teams
import user
from __init__ import LABEL_SERVER, MIN_DAYS, MAX_DAYS, MIN_LABELS, MAX_LABELS
from db import Settings
from inventory import Item
from sanitizer import VALIDATORS, MINMAX, sanitize, handle_api_exception, APIException
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


@api.route('/items', methods=['POST'])
@login_required(admin_only=True)
@handle_api_exception
def add_item() -> flask.Response:
    """Add an item to the database."""
    # START: Validation
    validation_map = {
        'id': VALIDATORS.UNIQUE_ID,
        'name': VALIDATORS.NAME,
        'category': VALIDATORS.CATEGORY,
    }
    item_dict = sanitize(validation_map, flask.request.form)
    # END: Validation

    item = Item(**item_dict)
    inventory.add(item)
    return flask.Response(f'La til {item.id} i databasen.', status=201)


@api.route('/items/<item_id>', methods=['PUT'])
@login_required(admin_only=True)
@handle_api_exception
def edit_item(item_id: str) -> flask.Response:
    """Edit an item in the database."""
    # START: Validation
    validation_map = {
        'id': VALIDATORS.UNIQUE_OR_SAME_ID,
        'name': VALIDATORS.NAME,
        'category': VALIDATORS.CATEGORY,
    }
    item_dict = sanitize(validation_map, flask.request.form, {'id': item_id})
    # END: Validation

    item = Item(**item_dict)
    inventory.edit(item_id, item)
    return flask.Response(f'Redigerte {item_id} i databasen.', status=200)


@api.route('/items/<item_id>', methods=['DELETE'])
@login_required(admin_only=True)
@handle_api_exception
def delete_item(item_id: str) -> flask.Response:
    """Delete an item from the database."""
    inventory.delete(item_id)
    return flask.Response(f'Slettet {item_id} fra databasen.', status=200)


@api.route('/items/<item_id>/label/<variant>/preview', methods=['GET'])
@login_required(admin_only=True)
@handle_api_exception
def get_label_preview(item_id: str, variant: str = 'qr') -> flask.Response:  # pragma: no cover
    """Get a label preview for an item."""
    item = inventory.get(item_id)
    url = f'{LABEL_SERVER}/preview?id={item.id}&name={item.name}&variant={variant}'
    return flask.redirect(url)


@api.route('/items/<item_id>/label/print', methods=['POST'])
@login_required(admin_only=True)
@handle_api_exception
def print_label(item_id: str) -> flask.Response:  # pragma: no cover
    # START: Validation
    validation_map = {
        'print_label_count': VALIDATORS.INT,
        'print_label_count_minmax': MINMAX(MIN_LABELS, MAX_LABELS),
        'print_label_type': VALIDATORS.LABEL_TYPE,
    }
    form = sanitize(validation_map, flask.request.form)
    # END: Validation

    variant = form.get('print_label_type', 'qr')
    count = int(form.get('print_label_count', '1'))
    item = inventory.get(item_id)
    url = f'{LABEL_SERVER}/print?id={item.id}&name={item.name}&variant={variant}&count={count}'
    try:
        response = requests.post(url, timeout=5)
    except requests.exceptions.RequestException as e:
        return flask.Response(str(e), status=500)
    return flask.Response(response.text, status=response.status_code)


@api.route('/book/out', methods=['POST'])
@login_required(admin_only=True)
@handle_api_exception
def book_equipment() -> flask.Response:
    """Book out equipment for a user."""
    # START: Validation
    validation_map = {
        'user': VALIDATORS.USER,
        'days': VALIDATORS.INT,
        'days_minmax': MINMAX(MIN_DAYS, MAX_DAYS),
        'equipment': VALIDATORS.ITEM_LIST_EXISTS,
    }
    form = sanitize(validation_map, flask.request.form)
    # END: Validation
    userid = form.get('user')
    days = form.get('days')

    for item in form.get('equipment'):
        inventory.register_out(item_id=item, userid=userid, days=days)
    return flask.Response(f'Utstyret ble utlevert til {user.get(userid).get("name")}.', status=200)


@api.route('/book/postpone', methods=['POST'])
@login_required(admin_only=True)
@handle_api_exception
def postpone_due_date() -> flask.Response:
    """Postpone the due date for an item."""
    # START: Validation
    validation_map = {
        'item_id': VALIDATORS.ID,
        'days': VALIDATORS.INT,
        'days_minmax': MINMAX(MIN_DAYS, MAX_DAYS),
    }
    form = sanitize(validation_map, flask.request.form)
    # END: Validation
    item_id = form.get('item_id')
    days = int(form.get('days'))
    inventory.postpone_due_date(item_id=item_id, days=days)
    return flask.Response(f'Fristen for {item_id} ble utsatt med {days} {"dager" if days > 1 else "dag"}.', status=200)


@api.route('/return/<item_id>', methods=['POST'])
@login_required(admin_only=True)
@handle_api_exception
def return_equipment(item_id: str) -> flask.Response:
    """Return equipment from a user."""
    inventory.register_in(item_id=item_id)
    return flask.Response('Utstyr ble innlevert.', status=200)


@api.route('/user/<userid>', methods=['GET'])
@login_required(admin_only=True, api=True)
def get_user(userid: str) -> flask.Response:
    """Get user as JSON."""
    u = user.get(userid)
    return flask.jsonify(u)


@api.route('/users', methods=['POST'])
@login_required()
def register_student() -> flask.Response:
    """Add/update a class in the database."""
    selected_classroom = flask.request.form.get('classroom')
    try:
        sanitize({'classroom': VALIDATORS.GROUP}, {'classroom': selected_classroom})
    except APIException as e:
        return flask.abort(e.status_code, e.message)

    data = {
        'name': flask.session.get('user').name,
        'email': flask.session.get('user').email,
        'userid': flask.session.get('user').userid,
        'classroom': selected_classroom,
        'updated_at': datetime.now().isoformat(),
        'expires_at': next_july().isoformat()
    }

    with db.connect() as (con, cur):
        cur.execute(
            'REPLACE INTO users (name, email, userid, classroom, updated_at, expires_at) '
            'VALUES (:name, :email, :userid, :classroom, :updated_at, :expires_at)',
            data)

    return flask.redirect(flask.request.referrer)


@api.route('/groups', methods=['PUT'])
@login_required(admin_only=True)
@handle_api_exception
def update_groups() -> flask.Response:
    """Update a class in the database."""
    new_groups = []
    for group in flask.request.form.get('groups').split('\n'):
        if not group.strip():
            continue
        sanitize({'group': VALIDATORS.GROUP_NAME}, {'group': group.strip()})
        new_groups.append(group.strip())

    with db.connect() as (con, cur):
        # noinspection SqlWithoutWhere
        cur.execute('DELETE FROM groups')
        con.commit()
        for group in new_groups:
            cur.execute('INSERT INTO groups (classroom) VALUES (?)', (group,))

    return flask.Response('Gruppene ble oppdatert.', status=200)


@api.route('/categories', methods=['PUT'])
@login_required(admin_only=True)
@handle_api_exception
def update_categories() -> flask.Response:
    """Update every category in the database."""
    new_categories = []
    for category in flask.request.form.get('categories').split('\n'):
        if not category.strip():
            continue
        sanitize({'category': VALIDATORS.CATEGORY_NAME}, {'category': category.strip()})
        new_categories.append(category.strip())

    with db.connect() as (con, cur):
        # noinspection SqlWithoutWhere
        cur.execute('DELETE FROM categories')
        con.commit()
        for category in new_categories:
            cur.execute('INSERT INTO categories (name) VALUES (?)', (category,))

    return flask.Response('Kategoriene ble oppdatert.', status=200)


@api.route('/registrer_avvik', methods=['POST'])
@login_required(admin_only=True)
@handle_api_exception
def registrer_avvik() -> flask.Response:
    """Log a defect."""
    item_id = flask.request.form.get('id') or ''
    log_text = flask.request.form.get('text') or ''

    if item_id:
        txt = f'Avvik på utstyr {item_id}: {log_text}'
    else:
        txt = f'Generelt avvik: {log_text}'

    audits.audit('AVVIK', markupsafe.escape(txt))
    teams.send_deviation(txt)
    return flask.Response('Avvik ble sendt til videre oppfølging', status=200)


@api.route('/send_report', methods=['POST'])
@login_required(admin_only=True, api=True)
@handle_api_exception
def send_report() -> flask.Response:  # pragma: no cover
    """Send a report to the specified teams webhooks.

    Can be used with a cron job to send reports automatically, e.g.:
    15 8 * 1-6,8-12 MON curl -X POST "http://localhost:5000/send_report?interval=7&token=<token>"

    If the interval parameter is set, the report will only be sent
    if the last report was sent more than interval days ago.
    """
    interval = flask.request.args.get('interval')

    if interval:
        sanitize({'interval': VALIDATORS.INT}, flask.request.args)
        current_date = datetime.now().date()
        last_sent = datetime.fromtimestamp(float(Settings.get('report_last_sent') or 0)).date()
        if last_sent and (current_date - last_sent).days < int(interval):
            raise APIException(f'Ikke sendt - mindre enn {interval} dager siden forrige rapport.', 200)

    return teams.send_report()


@api.route('/users/me', methods=['DELETE'])
@login_required()
def delete_me() -> flask.Response:
    """Delete the currently logged in user."""
    u = flask.session.get("user")
    user.delete(u.userid)
    flask.session.clear()
    return flask.Response(f'Bruker {u.name} ble slettet.', status=200)


@api.route('/bulletin', methods=['PUT'])
@login_required(admin_only=True)
@handle_api_exception
def update_bulletin() -> flask.Response:
    """Update the bulletin."""
    bulletin_title = flask.request.form.get('bulletin_title') or ''
    bulletin = flask.request.form.get('bulletin') or ''

    Settings.set('bulletin_title', markupsafe.escape(bulletin_title))
    Settings.set('bulletin', markupsafe.escape(bulletin))
    return flask.Response('Bulletin ble oppdatert.', status=200)


@api.route('/toggle-reports', methods=['POST'])
@login_required(admin_only=True)
@handle_api_exception
def update_send_reports() -> flask.Response:
    """Toggles the send_reports setting in the database."""
    send_reports = Settings.get('send_reports') == '1'
    Settings.set('send_reports', '0' if send_reports else '1')
    return flask.Response('Dagsrapporter er nå slått ' + ('av' if send_reports else 'på') + '.', status=200)

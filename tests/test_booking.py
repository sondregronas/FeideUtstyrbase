import uuid
from datetime import datetime, timedelta

from dateutil.parser import parse

import db
import inventory
from __init__ import MAX_DAYS
from conftest import *
from test_items import generate_item
from test_user import add_classroom


class ctx_booking:
    def __init__(self, client, users: int, items: int):
        self.client = client
        self.users = [StudentUser(userid=str(uuid.uuid4())) for _ in range(users)]
        self.items = [generate_item() for _ in range(items)]
        add_classroom(client)
        for item in self.items:
            inventory.add(item)
        with client.session_transaction() as session:
            old = session['user']
        for user in self.users:
            with client.session_transaction() as session:
                session['user'] = user
            client.post(url_for(client, 'api.register_student'),
                        data={'classroom': 'Classroom (Teacher Name)'})
        with client.session_transaction() as session:
            session['user'] = old

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup users
        for user in self.users:
            with self.client.session_transaction() as session:
                old = session['user']
                session['user'] = user
            self.client.delete(url_for(self.client, 'api.delete_me'))
            with self.client.session_transaction() as session:
                session['user'] = old
        # Cleanup items
        for item in self.items:
            inventory.delete(item_id=item.id)


def test_booking(admin_client):
    with ctx_booking(admin_client, 5, 5) as ctx:
        # Verify that all users show up on the booking page (userid is in the HTML)
        r = admin_client.get(url_for(admin_client, 'app.booking'))
        assert r.status_code == 200
        for user in ctx.users:
            assert user.userid in r.data.decode('utf-8')


def test_booking_item(admin_client):
    with ctx_booking(admin_client, 5, 5) as ctx:

        # Who and what to book
        user = ctx.users[0]
        equipment = [ctx.items[0], ctx.items[1]]

        # Construct the booking data
        data = {'user': user.userid, 'days': '1', 'equipment': [item.id for item in equipment]}

        # Verify that the user has no items
        r = admin_client.get(url_for(admin_client, 'api.get_items_by_userid', userid=ctx.users[0].userid))
        assert not r.json
        for item in equipment:
            assert item.id not in [i['id'] for i in
                                   admin_client.get(url_for(admin_client, 'api.get_items_unavailable')).json]
            assert item.id in [i['id'] for i in
                               admin_client.get(url_for(admin_client, 'api.get_items_available')).json]

        # Book the items
        r = admin_client.post(url_for(admin_client, 'api.book_equipment'), data=data)
        assert r.status_code == 200

        # Verify that the user has the items
        r = admin_client.get(url_for(admin_client, 'api.get_items_by_userid', userid=ctx.users[0].userid))
        for item in equipment:
            assert item.id in [i['id'] for i in r.json]
            assert user.userid in [i['borrowed_to'] for i in r.json]

            assert item.id in [i['id'] for i in
                               admin_client.get(url_for(admin_client, 'api.get_items_unavailable')).json]
            assert item.id not in [i['id'] for i in
                                   admin_client.get(url_for(admin_client, 'api.get_items_available')).json]


def test_booking_item_wrong_date(admin_client):
    with ctx_booking(admin_client, 5, 5) as ctx:
        user = ctx.users[0]
        equipment = [ctx.items[0], ctx.items[1]]
        data = {'user': user.userid, 'days': '0', 'equipment': [item.id for item in equipment]}

        r = admin_client.post(url_for(admin_client, 'api.book_equipment'), data=data)
        assert r.status_code == 400

        data['days'] = 'a'
        r = admin_client.post(url_for(admin_client, 'api.book_equipment'), data=data)
        assert r.status_code == 400

        # Above MAX_DAYS
        data['days'] = str(MAX_DAYS + 1)
        r = admin_client.post(url_for(admin_client, 'api.book_equipment'), data=data)
        assert r.status_code == 400

        # Below 0
        data['days'] = str(-1)
        r = admin_client.post(url_for(admin_client, 'api.book_equipment'), data=data)
        assert r.status_code == 400

        # No days
        del data['days']
        r = admin_client.post(url_for(admin_client, 'api.book_equipment'), data=data)
        assert r.status_code == 400


def test_booking_item_wrong_user(admin_client):
    with ctx_booking(admin_client, 5, 5) as ctx:
        user = ctx.users[0]
        equipment = [ctx.items[0], ctx.items[1]]
        data = {'user': user.userid, 'days': '1', 'equipment': [item.id for item in equipment]}

        # Wrong user
        data['user'] = 'not a user'
        r = admin_client.post(url_for(admin_client, 'api.book_equipment'), data=data)
        assert r.status_code == 400

        # No user
        del data['user']
        r = admin_client.post(url_for(admin_client, 'api.book_equipment'), data=data)
        assert r.status_code == 400


def test_booking_item_wrong_equipment(admin_client):
    with ctx_booking(admin_client, 5, 5) as ctx:
        user = ctx.users[0]
        equipment = [ctx.items[0], ctx.items[1]]
        data = {'user': user.userid, 'days': '1', 'equipment': [item.id for item in equipment]}

        # Wrong equipment
        data['equipment'] = ['not an item']
        r = admin_client.post(url_for(admin_client, 'api.book_equipment'), data=data)
        assert r.status_code == 400

        # No equipment
        del data['equipment']
        r = admin_client.post(url_for(admin_client, 'api.book_equipment'), data=data)
        assert r.status_code == 400


def test_postpone_equipment(admin_client):
    with ctx_booking(admin_client, 5, 5) as ctx:
        user = ctx.users[0]
        equipment = [ctx.items[0]]
        data = {'user': user.userid, 'days': '1', 'equipment': [item.id for item in equipment]}

        # Book the items
        r = admin_client.post(url_for(admin_client, 'api.book_equipment'), data=data)

        # Verify that due date is one day from now
        r = admin_client.get(url_for(admin_client, 'api.get_items_by_userid', userid=ctx.users[0].userid))
        one_day_from_now = datetime.now() + timedelta(days=1)
        due_dates = [parse(i['order_due_date']).strftime('%Y-%m-%d') for i in r.json]
        assert one_day_from_now.strftime('%Y-%m-%d') in due_dates

        # Postpone the item (to two days from now)
        data = {'item_id': equipment[0].id, 'days': '2'}
        admin_client.post(url_for(admin_client, 'api.postpone_due_date'), data=data)

        # Verify that due date is two days from now
        r = admin_client.get(url_for(admin_client, 'api.get_items_by_userid', userid=ctx.users[0].userid))
        two_days_from_now = datetime.now() + timedelta(days=2)
        due_dates = [parse(i['order_due_date']).strftime('%Y-%m-%d') for i in r.json]
        assert two_days_from_now.strftime('%Y-%m-%d') in due_dates

        # Verify that you cannot postpone in negative days or above MAX_DAYS
        data['days'] = '-1'
        r = admin_client.post(url_for(admin_client, 'api.postpone_due_date'), data=data)
        assert r.status_code == 400

        data['days'] = str(MAX_DAYS + 1)
        r = admin_client.post(url_for(admin_client, 'api.postpone_due_date'), data=data)
        assert r.status_code == 400


def test_returning_wrong_id(admin_client):
    r = admin_client.post(url_for(admin_client, 'api.return_equipment', item_id='this is not an id'))
    assert r.status_code == 400


def test_booking_and_returning(admin_client):
    with ctx_booking(admin_client, 5, 5) as ctx:
        user = ctx.users[0]
        equipment = [ctx.items[0], ctx.items[1]]
        data = {'user': user.userid, 'days': '1', 'equipment': [item.id for item in equipment]}

        # Book the items
        r = admin_client.post(url_for(admin_client, 'api.book_equipment'), data=data)

        # Verify that the user has the items
        r = admin_client.get(url_for(admin_client, 'api.get_items_by_userid', userid=ctx.users[0].userid))
        for item in equipment:
            assert item.id in [i['id'] for i in r.json]
            assert user.userid in [i['borrowed_to'] for i in r.json]

            assert item.id in [i['id'] for i in
                               admin_client.get(url_for(admin_client, 'api.get_items_unavailable')).json]
            assert item.id not in [i['id'] for i in
                                   admin_client.get(url_for(admin_client, 'api.get_items_available')).json]

        # Return one item
        r = admin_client.post(url_for(admin_client, 'api.return_equipment', item_id=equipment[0].id))
        assert r.status_code == 200

        # Verify that the item is returned
        r = admin_client.get(url_for(admin_client, 'api.get_items_by_userid', userid=ctx.users[0].userid))
        assert equipment[0].id not in [i['id'] for i in r.json]

        # Verify that the item is available
        assert equipment[0].id not in [i['id'] for i in
                                       admin_client.get(url_for(admin_client, 'api.get_items_unavailable')).json]
        assert equipment[0].id in [i['id'] for i in
                                   admin_client.get(url_for(admin_client, 'api.get_items_available')).json]


def test_booking_same_item_multiple_users(admin_client):
    """Make sure that the same item will switch between the user when booked before getting returned"""
    with ctx_booking(admin_client, 5, 5) as ctx:
        user = ctx.users[0]
        equipment = [ctx.items[0]]
        data = {'user': user.userid, 'days': '1', 'equipment': [item.id for item in equipment]}

        r = admin_client.post(url_for(admin_client, 'api.book_equipment'), data=data)
        assert r.status_code == 200

        # Verify that the user has the item
        r = admin_client.get(url_for(admin_client, 'api.get_items_by_userid', userid=ctx.users[0].userid))
        assert equipment[0].id in [i['id'] for i in r.json]
        assert user.userid in [i['borrowed_to'] for i in r.json]

        # Book the item for another user
        data['user'] = ctx.users[1].userid
        r = admin_client.post(url_for(admin_client, 'api.book_equipment'), data=data)
        assert r.status_code == 200

        # Verify that the user has the item
        r = admin_client.get(url_for(admin_client, 'api.get_items_by_userid', userid=ctx.users[1].userid))
        assert equipment[0].id in [i['id'] for i in r.json]
        assert ctx.users[1].userid in [i['borrowed_to'] for i in r.json]

        # Verify that the old user does not have the item
        r = admin_client.get(url_for(admin_client, 'api.get_items_by_userid', userid=ctx.users[0].userid))
        assert equipment[0].id not in [i['id'] for i in r.json]


def test_booking_overdue(admin_client):
    with ctx_booking(admin_client, 5, 5) as ctx:
        user = ctx.users[0]
        equipment = [ctx.items[0], ctx.items[1]]
        data = {'user': user.userid, 'days': '1', 'equipment': [item.id for item in equipment]}
        r = admin_client.post(url_for(admin_client, 'api.book_equipment'), data=data)
        assert r.status_code == 200

        item = inventory.get(equipment[0].id)
        assert not item.overdue
        assert equipment[0].id not in [i['id'] for i in
                                       admin_client.get(url_for(admin_client, 'api.get_items_overdue')).json]

        # Verify that the item is not displayed on the front page (when logged in as admin)
        assert 'overdue_items' not in admin_client.get(url_for(admin_client, 'app.index')).text

        # Set due date to yesterday
        sql = 'UPDATE inventory SET order_due_date=:order_due_date WHERE id=:id'
        with db.connect() as (conn, cur):
            cur.execute(sql, {'order_due_date': str(datetime.now() - timedelta(days=2)), 'id': item.id})
        item = inventory.get(equipment[0].id)

        # Verify that the item is overdue
        assert item.overdue
        assert equipment[0].id in [i['id'] for i in
                                   admin_client.get(url_for(admin_client, 'api.get_items_overdue')).json]

        # Verify that the item is displayed on the front page (when logged in as admin)
        assert 'overdue_items' in admin_client.get(url_for(admin_client, 'app.index')).text

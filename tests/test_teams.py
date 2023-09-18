import uuid
from datetime import datetime

import audits
import db
from conftest import *
from sanitizer import APIException
from teams import get_overdue_card, get_deviation_card, last_sent_within_hour_treshold, formatted_new_deviations, \
    formatted_overdue_items
from test_items import generate_item


def test_generate_overdue_card():
    item = generate_item()
    c = get_overdue_card([item])
    assert item.html_repr() in c.payload['text']


def test_generate_deviations_card(admin_client):
    noid_data = {
        'id': None,
        'text': f'Testavvik uten ID ({str(uuid.uuid4())})',
    }
    noid_expected = f'Generelt avvik: {noid_data["text"]}'

    id_data = {
        'id': str(uuid.uuid4()),
        'text': 'Testavvik med ID',
    }
    id_expected = f'Avvik på utstyr {id_data["id"]}: {id_data["text"]}'

    last_sent = db.Settings.get('report_last_sent') or 0

    c = get_deviation_card(audits.get_new_deviations(since=last_sent))
    assert noid_expected not in c.payload['text']
    assert id_expected not in c.payload['text']

    admin_client.post(url_for(admin_client, 'api.registrer_avvik'), data=noid_data)
    admin_client.post(url_for(admin_client, 'api.registrer_avvik'), data=id_data)

    c = get_deviation_card(audits.get_new_deviations(since=last_sent))
    assert noid_expected in c.payload['text']
    assert id_expected in c.payload['text']


def test_empty_formatted_cards():
    assert not formatted_new_deviations([])
    assert not formatted_overdue_items([])


def test_last_sent_limit():
    now = datetime.now().timestamp()

    db.Settings.set('report_last_sent', str(now))
    with pytest.raises(APIException):
        last_sent_within_hour_treshold()  # raises exception if last_sent is within an hour

    db.Settings.set('report_last_sent', str(now - 3600))
    assert last_sent_within_hour_treshold()  # returns last_sent

    db.Settings.set('report_last_sent', str(now - 3500))
    with pytest.raises(APIException):
        last_sent_within_hour_treshold()  # raises exception if last_sent is within an hour

from datetime import datetime

import db
from conftest import *
from sanitizer import APIException
from teams import get_overdue_card, last_sent_within_hour_treshold, formatted_overdue_items
from test_items import generate_item


def test_generate_overdue_card():
    item = generate_item()
    c = get_overdue_card([item])
    assert item.html_repr() in c.payload['text']


def test_empty_formatted_cards():
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

"""
Test a couple of endpoints that arent covered by the other tests.
"""

from conftest import *
from test_booking import ctx_booking


def test_print_itemid(admin_client):
    with ctx_booking(admin_client, 5, 5) as ctx:
        r = admin_client.get(url_for(admin_client, 'app.print_item', item_id=ctx.items[0].id))
        assert r.status_code == 200
        assert r.data
        assert ctx.items[0].id in r.data.decode('utf-8')

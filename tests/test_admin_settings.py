import uuid

import inventory
from conftest import *


def test_update_categories_invalid(admin_client):
    r = admin_client.put(url_for(admin_client, 'api.update_categories'),
                         data={'categories': '¤%&/()=?`´¨^*#'})
    assert r.status_code == 400


def test_update_categories(admin_client):
    old_categories = inventory.all_categories()

    r = admin_client.put(url_for(admin_client, 'api.update_categories'),
                         data={'categories': 'Category1\nCategory2\nCategory3\n'})
    assert r.status_code == 200

    new_categories = inventory.all_categories()
    assert new_categories == ['Category1', 'Category2', 'Category3']

    # Restore the old categories
    r = admin_client.put(url_for(admin_client, 'api.update_categories'),
                         data={'categories': '\n'.join(old_categories)})
    assert r.status_code == 200
    assert inventory.all_categories() == old_categories


def test_update_groups_invalid(admin_client):
    r = admin_client.put(url_for(admin_client, 'api.update_groups'),
                         data={'groups': '¤%&/()=?`´¨^*#'})
    assert r.status_code == 400


def test_update_bulletin(admin_client):
    bulletin_title = str(uuid.uuid4())
    bulletin = f'This is a test bulletin. ({str(uuid.uuid4())})'
    r = admin_client.put(url_for(admin_client, 'api.update_bulletin'), data={'bulletin_title': bulletin_title,
                                                                             'bulletin': bulletin})

    assert r.status_code == 200

    r = admin_client.get(url_for(admin_client, 'app.index'))
    assert bulletin_title in r.data.decode('utf-8')
    assert bulletin in r.data.decode('utf-8')


def test_update_bulletin_html_injection(admin_client):
    bulletin_title = '<script>alert("XSS")</script>'
    bulletin = '<script>alert("XSS")</script>'
    r = admin_client.put(url_for(admin_client, 'api.update_bulletin'), data={'bulletin_title': bulletin_title,
                                                                             'bulletin': bulletin})
    assert r.status_code == 200

    r = admin_client.get(url_for(admin_client, 'app.index'))
    assert bulletin_title not in r.data.decode('utf-8')
    assert bulletin not in r.data.decode('utf-8')
    assert '&lt;script&gt;alert(&#34;XSS&#34;)&lt;/script&gt;' in r.data.decode('utf-8')

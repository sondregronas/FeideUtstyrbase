import uuid

from conftest import *
from inventory import get, Item
from sanitizer import APIException


def all_items(client) -> list[Item]:
    """Helper function to get all items."""
    for item in client.get(url_for(client, 'api.get_items')).json:
        yield Item(**item)


def generate_item(name: str = 'Test item') -> Item:
    """Helper function to generate a random item."""
    data = {
        'id': str(uuid.uuid4()),
        'name': name,
        'category': 'PC',
    }
    return Item(**data)


def test_add_item(admin_client):
    item = generate_item()
    admin_client.post(url_for(admin_client, 'api.add_item'), data=item.__dict__)

    assert item.name == get(item.id).name
    assert get(item.id).id in [item.id for item in all_items(admin_client)]


def test_add_item_duplicate(admin_client):
    item = generate_item()
    r = admin_client.post(url_for(admin_client, 'api.add_item'), data=item.__dict__)
    assert r.status_code == 201
    r = admin_client.post(url_for(admin_client, 'api.add_item'), data=item.__dict__)
    assert r.status_code == 400


def test_edit_item(admin_client):
    # Add item
    original_name = str(uuid.uuid4())
    item = generate_item(name=original_name)
    admin_client.post(url_for(admin_client, 'api.add_item'), data=item.__dict__)

    # Ensure name is in database
    assert get(item.id).name == item.name
    assert original_name in [item.name for item in all_items(admin_client)]

    # Create new item with same id, but different name
    old_item_values = item.__dict__.copy()
    old_item_values.pop('name')
    new_item = Item(name='New name', **old_item_values)

    # Edit item
    admin_client.put(url_for(admin_client, "api.edit_item", item_id=item.id), data=new_item.__dict__)

    # Ensure name is changed
    assert get(item.id).name == new_item.name
    assert original_name not in [item.name for item in all_items(admin_client)]


def test_delete_item(admin_client):
    # Add item
    item = generate_item()
    admin_client.post(url_for(admin_client, 'api.add_item'), data=item.__dict__)

    # Ensure item is in database
    assert get(item.id).name == item.name
    assert get(item.id) in all_items(admin_client)

    # Delete item
    admin_client.delete(url_for(admin_client, 'api.delete_item', item_id=item.id))

    # Ensure item is not in database
    with pytest.raises(APIException):
        get(item.id)
    assert item.id not in [item.id for item in all_items(admin_client)]

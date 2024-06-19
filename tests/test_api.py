import os

import pytest

from conftest import *


@pytest.mark.skip(reason='Using a scheduler to run the backup now, so this test needs modification.')
def test_backup_invalid(admin_client):
    r = admin_client.post(url_for(admin_client, 'api.backup', filename='b.invalid'))
    assert r.status_code == 400

    r = admin_client.post(url_for(admin_client, 'api.backup', filename='invalid'))
    assert r.status_code == 400


@pytest.mark.skip(reason='Using a scheduler to run the backup now, so this test needs modification.')
def test_backup(admin_client):
    db = Path('data/db.sqlite').resolve()
    backup = Path('data/backups/test_backup.sqlite').resolve()

    assert not os.path.exists(backup)

    r = admin_client.post(url_for(admin_client, 'api.backup', filename='test_backup.sqlite'))
    assert r.status_code == 200

    assert os.path.exists(backup)
    assert os.path.getsize(backup) == os.path.getsize(db)

    os.remove(backup)
    try:
        os.rmdir(backup.parent)
    except OSError:
        pass

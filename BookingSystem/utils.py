from datetime import datetime
from functools import wraps

import flask

from __init__ import API_TOKEN
from feide import get_feide_data
from user import User, FeideUser, KioskUser


def user_factory() -> User | None:
    """Create a user object based on the session data."""
    match flask.session.get('method'):
        case 'feide':
            return FeideUser(**get_feide_data())
        case 'kiosk':
            return KioskUser(name='Kiosk', email='', userid='kiosk', affiliations=[])
        case _:
            return None


def refresh_user() -> None:
    """Update the session with the latest user data."""
    if flask.session.get('user'):
        flask.session['user'].update()
    else:
        flask.session['user'] = user_factory()


def login_required(admin_only: bool = False, api: bool = False) -> callable:
    """Decorator to check if the user is logged in."""

    def decorator(func: callable) -> callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> callable:
            if api and API_TOKEN:
                if flask.request.args.get('token') == API_TOKEN:
                    return func(*args, **kwargs)
            refresh_user()
            user = flask.session.get('user')
            if not user:
                flask.abort(401)
            if admin_only and not user.is_admin:
                flask.abort(403)
            return func(*args, **kwargs)

        wrapper.login_required = True
        wrapper.admin_required = admin_only
        wrapper.api_allowed = api
        return wrapper

    return decorator


def next_july() -> datetime:
    """Get the first coming July 1st. (End of school year)"""
    expiry_date = datetime(datetime.now().year, 7, 1)
    if datetime.now() > expiry_date:
        expiry_date = datetime(datetime.now().year + 1, 7, 1)
    return expiry_date


def get_audits() -> list[dict]:
    """Get the logs from the audit log."""
    log = open('data/audits.log', 'r').readlines()
    return [{
        'timestamp': audit.split('|')[0].strip(),
        'event': audit.split('|')[1].split(' - ')[0].strip(),
        'message': ''.join(audit.split(' - ')[1:]).strip()
    } for audit in log if audit.strip()]

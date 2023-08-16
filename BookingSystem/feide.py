"""
This module handles the Feide login and the Feide API.

Everything is done via Authlib, which is a library that handles OAuth2 and OpenID Connect.

utils.py calls the `refresh_user` function on every request, which updates the session with the latest user data.
Should the data be invalid the session will clear and the user gets redirected to the login page. (401)
"""

import os
from functools import wraps

import flask
import requests
from authlib.integrations.base_client.errors import AuthlibBaseError
from authlib.integrations.flask_client import OAuth

from __init__ import logger

feide = flask.Blueprint('feide', __name__)

oauth = OAuth(flask.current_app)
oauth.register(
    name='feide',
    client_id=os.getenv('FEIDE_CLIENT_ID'),
    client_secret=os.getenv('FEIDE_CLIENT_SECRET'),
    access_token_url='https://auth.dataporten.no/oauth/token',
    access_token_params=None,
    authorize_url='https://auth.dataporten.no/oauth/authorization',
    authorize_params=None,
    api_base_url='https://auth.dataporten.no/',
    client_kwargs={'scope': 'groups-org userinfo-name email'},
)


def handle_auth_exception(f) -> callable:
    """Handle exceptions that may occur during the authorization process."""

    @wraps(f)
    def wrapper(*args, **kwargs) -> callable:
        try:
            return f(*args, **kwargs)
        except(KeyError, AttributeError):
            logger.warning(f'Unauthorized access: {flask.request.url} from {flask.request.remote_addr}')
            flask.session.clear()
            flask.abort(401)
        except AuthlibBaseError:
            logger.error(f'Authlib error: {flask.request.url} from {flask.request.remote_addr}')
            flask.session.clear()
            flask.abort(500)
        except(requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
            logger.error(f'Connection error: {flask.request.url} from {flask.request.remote_addr}')
            flask.abort(500)

    return wrapper


@feide.route('/login/feide')
def login() -> flask.Response:
    """Redirect the user to the Feide login page."""
    feide_oauth = oauth.create_client('feide')
    redirect_uri = os.getenv('FEIDE_REDIRECT_URI')
    return feide_oauth.authorize_redirect(redirect_uri)


@feide.route('/login/feide/callback')
@handle_auth_exception
def callback() -> flask.Response:
    """Authorize the user and redirect them to the index page."""
    feide_oauth = oauth.create_client('feide')
    token = feide_oauth.authorize_access_token()
    if not token:
        raise KeyError
    flask.session['feide_token'] = token
    flask.session['method'] = 'feide'
    feide_oauth.get('https://groups-api.dataporten.no/groups/me/groups').json()
    return flask.redirect(flask.url_for('app.register'))


@handle_auth_exception
def get_feide_data() -> dict:
    """
    Return a dict with the user's name, email, userid and affiliations.

    Used by @login_required to get the user's data (or kick them out if they're not a valid user).
    (See utils.py for more info on @login_required.)
    """
    feide_oauth = oauth.create_client('feide')
    feide_oauth.token = flask.session.get('feide_token')
    userinfo = feide_oauth.get('userinfo').json()
    groups = feide_oauth.get('https://groups-api.dataporten.no/groups/me/groups').json()
    return {
        'name': userinfo['user']['name'],
        'email': userinfo['user']['email'],
        'userid': userinfo['user']['userid'],
        'affiliations': groups[0]['membership']['affiliation']
    }

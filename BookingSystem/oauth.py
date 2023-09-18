import os
from functools import wraps

import flask
import requests
from authlib.integrations.base_client.errors import AuthlibBaseError
from authlib.integrations.flask_client import OAuth

from __init__ import logger

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


def handle_oauth_exception(f) -> callable:  # pragma: no cover
    """
    Handle exceptions that may occur during the authorization process.

    Should the user not be authorized, the session will clear and the user gets redirected to the login page. (401)
    """

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

import os

import flask
import requests

from __init__ import logger

"""
Upon successful authentication, the user's data is saved in the session.

session['method'] = 'feide'
session['feide_token'] = '123456-abcdef'

Inside utils.py, the function refresh_user() is called to update the session with the latest user data,
this gets updated every time a page that requires authentication is loaded (depending on the method);

Example:
session['user'] = {
    'name': 'John Doe',
    'email': 'johndoe@example.com',
    'userid': '123456',
    'affiliation': ['employee', 'admin']
}
"""

# page to redirect to after successful authentication
POST_AUTH_PAGE = 'register'  # (flask.url_for)

"""
Routes / blueprint for FEIDE login.
"""

FEIDE_CLIENT_ID = os.getenv('FEIDE_CLIENT_ID')
FEIDE_CLIENT_SECRET = os.getenv('FEIDE_CLIENT_SECRET')
FEIDE_REDIRECT_URI = os.getenv('FEIDE_REDIRECT_URI')

feide = flask.Blueprint('feide', __name__)


@feide.route('/login/feide', methods=['GET'], endpoint='login')
def login_feide() -> flask.Response:
    """Redirect to FEIDE's endpoint for login."""
    return flask.redirect(
        f'https://auth.dataporten.no/oauth/authorization?response_type=code&client_id={FEIDE_CLIENT_ID}&redirect_uri={FEIDE_REDIRECT_URI}')


@feide.route('/login/feide/callback', methods=['GET'])
def login_feide_callback() -> flask.Response:
    """Callback from FEIDE, save method & token in the session then redirect to register page. (Regardless of whether the user is already registered or not.)"""
    code = flask.request.args.get('code')
    if not code:
        logger.error('No code in callback!')
        flask.abort(401)
    flask.session['method'] = 'feide'
    flask.session['feide_token'] = _get_feide_token(code)
    return flask.redirect(flask.url_for(POST_AUTH_PAGE))


"""
Functions for FEIDE login.

get_feide_data() - returns a dict with the user's data from FEIDE, 
                   and is the only function that should be called fromoutside this file.
"""


def get_feide_data() -> dict:
    """Get relevant user info from FEIDE."""
    data = _get_feide_userinfo()
    data['affiliations'] = _get_feide_affiliations()
    return data


def _get_feide_token(code: str) -> str:
    """Get a token from FEIDE."""
    url = 'https://auth.dataporten.no/oauth/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'authorization_code',
        'redirect_uri': FEIDE_REDIRECT_URI,
        'code': code,
        'client_id': FEIDE_CLIENT_ID,
        'client_secret': FEIDE_CLIENT_SECRET
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code != 200:
        logger.error(f'Error getting FEIDE token: {response.status_code} {response.text}')
        flask.abort(401)
    return response.json().get('access_token')


def _query(url: str) -> dict:
    """Query a URL, return the response as JSON."""
    headers = {'Authorization': f'Bearer {flask.session.get("feide_token")}'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logger.error(f'Error querying FEIDE: {response.status_code} {response.text}')
        flask.abort(401)
    return response.json()


def _get_feide_affiliations() -> list[str]:
    """Get affiliation from FEIDE."""
    url = 'https://groups-api.dataporten.no/groups/me/groups'
    return _query(url)[0]['membership']['affiliation']


def _get_feide_userinfo() -> dict:
    """Get user info from FEIDE."""
    url = 'https://auth.dataporten.no/userinfo'
    data = _query(url).get('user')
    return {
        'name': data.get('name'),
        'email': data.get('email'),
        'userid': data.get('userid')
    }

"""
This module handles the Feide login and the Feide API.

Everything is done via Authlib, which is a library that handles OAuth2 and OpenID Connect.

utils.py calls the `refresh_user` function on every request, which updates the session with the latest user data.
Should the data be invalid the session will clear and the user gets redirected to the login page. (401)
"""

import os

import flask

from oauth import oauth, handle_oauth_exception

feide = flask.Blueprint('feide', __name__)


@feide.route('/login/feide')
def login() -> flask.Response:  # pragma: no cover
    """Redirect the user to the Feide login page."""
    feide_oauth = oauth.create_client('feide')
    redirect_uri = os.getenv('FEIDE_REDIRECT_URI')
    return feide_oauth.authorize_redirect(redirect_uri)


@feide.route('/login/feide/callback')
@handle_oauth_exception
def callback() -> flask.Response:  # pragma: no cover
    """Authorize the user and redirect them to the index page."""
    feide_oauth = oauth.create_client('feide')
    token = feide_oauth.authorize_access_token()
    if not token:
        raise KeyError
    flask.session['feide_token'] = token
    flask.session['method'] = 'feide'
    return flask.redirect(flask.url_for('app.register'))


@handle_oauth_exception
def get_feide_data() -> dict:  # pragma: no cover
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

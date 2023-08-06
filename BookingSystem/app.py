import os
from datetime import datetime

import flask
from dateutil import parser
from flask_session import Session
from werkzeug.middleware.proxy_fix import ProxyFix

import api
import feide
import routes
from __init__ import logger
from db import init_db


def create_app() -> flask.Flask:
    # Flask app setup
    app = flask.Flask(__name__, template_folder='templates', static_folder='static')
    app.secret_key = os.getenv('SECRET_KEY')
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600
    if os.getenv('DEBUG') == 'True':
        app.debug = True

    # We're behind a reverse proxy, so we need to fix the scheme and host
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    Session(app)

    # Register blueprints
    app.register_blueprint(api.api)
    app.register_blueprint(feide.feide)
    app.register_blueprint(routes.app)

    @app.template_filter('strftime')
    def _jinja2_filter_datetime(date, fmt='%d.%m.%Y') -> str:
        return parser.parse(date).strftime(fmt)

    @app.template_filter('strfunixtime')
    def _jinja2_filter_strftime(date, fmt='%d.%m.%Y') -> str:
        return datetime.fromtimestamp(float(date)).strftime(fmt)

    @app.errorhandler(401)
    def unauthorized(_) -> flask.Response:
        logger.warning(f'Unauthorized access: {flask.request.url} from {flask.request.remote_addr}')
        return flask.redirect(flask.url_for('app.login'))

    @app.errorhandler(403)
    def unauthorized(_) -> flask.Response:
        flask.session.clear()
        logger.warning(f'Unauthorized access: {flask.request.url} from {flask.request.remote_addr}')
        return flask.redirect(flask.url_for('app.login'))

    return app


if __name__ == '__main__':
    init_db()
    create_app().run(host='0.0.0.0')

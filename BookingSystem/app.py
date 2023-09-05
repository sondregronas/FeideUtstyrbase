import os
from datetime import datetime
from urllib.parse import urlparse

import flask
from dateutil import parser
from flask_minify import Minify
from flask_session import Session
from werkzeug.middleware.proxy_fix import ProxyFix

import api
import audits
import feide
import groups
import inventory
import routes
import user
from __init__ import logger, REGEX_ID, REGEX_ITEM, MIN_DAYS, MAX_DAYS, MIN_LABELS, MAX_LABELS
from db import init_db, Settings


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

    # Minify
    Minify(app=app, static=False)

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

    @app.template_filter('unixtime')
    def _jinja2_filter_unixtime(date) -> int:
        return int(parser.parse(date, dayfirst=True).timestamp())

    @app.template_filter('split')
    def _jinja2_filter_split(string, split_char=',') -> list:
        return string.split(split_char)

    @app.context_processor
    def context_processor() -> dict:
        return dict(regex_id=REGEX_ID,
                    regex_item=REGEX_ITEM,
                    groups=groups.get_all(),
                    bulletin_title=Settings.get('bulletin_title'),
                    bulletin=Settings.get('bulletin'),
                    categories=inventory.all_categories(),
                    audits=audits.get_all(),
                    items=inventory.get_all(),
                    used_ids=inventory.get_all_ids(),
                    users=user.get_all_active_users(),
                    unavailable_items=inventory.get_all_unavailable(),
                    overdue_items=inventory.get_all_overdue(),
                    MIN_DAYS=MIN_DAYS,
                    MAX_DAYS=MAX_DAYS,
                    MIN_LABELS=MIN_LABELS,
                    MAX_LABELS=MAX_LABELS,
                    FQDN=urlparse(flask.request.base_url).hostname, )

    @app.errorhandler(401)
    def unauthorized(_) -> flask.Response:
        flask.session.clear()
        if flask.request.url != flask.url_for('app.index', _external=True):
            logger.warning(f'Unauthorized access: {flask.request.url} from {flask.request.remote_addr}')
        return flask.redirect(flask.url_for('app.login'))

    @app.errorhandler(403)
    def unauthorized(_) -> flask.Response:
        flask.session.clear()
        if flask.request.url != flask.url_for('app.index', _external=True):
            logger.warning(f'Unauthorized access: {flask.request.url} from {flask.request.remote_addr}')
        return flask.redirect(flask.url_for('app.login'))

    @app.errorhandler(404)
    def page_not_found(_) -> str:
        return flask.render_template('404.html')

    @app.errorhandler(418)
    def teapot(_) -> flask.Response:
        return flask.redirect('https://www.youtube.com/watch?v=dQw4w9WgXcQ')

    @app.errorhandler(500)
    def internal_server_error(_) -> str:
        return flask.render_template('500.html')

    # robots.txt
    @app.route('/robots.txt')
    def robots() -> flask.Response:
        return flask.send_from_directory(app.static_folder, 'robots.txt')

    return app


if __name__ == '__main__':
    init_db()
    create_app().run(host='0.0.0.0')
else:
    init_db()
    app = create_app()

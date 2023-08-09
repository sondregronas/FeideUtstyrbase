import os
from datetime import datetime

import flask
from dateutil import parser
from werkzeug.middleware.proxy_fix import ProxyFix

import api
import audits
import feide
import groups
import inventory
import mail
import routes
import user
from __init__ import logger, REGEX_ITEM, MIN_DAYS, MAX_DAYS, MIN_LABELS, MAX_LABELS
from db import init_db
from flask_session import Session


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

    @app.template_filter('split')
    def _jinja2_filter_split(string, split_char=',') -> list:
        return string.split(split_char)

    @app.context_processor
    def context_processor() -> dict:
        return dict(regex_item=REGEX_ITEM,
                    groups=groups.get_all(),
                    categories=inventory.all_categories(),
                    emails=mail.get_all_emails(),
                    audits=audits.get_all(),
                    items=inventory.get_all(),
                    used_ids=inventory.get_all_ids(),
                    users=user.get_all_active_users(),
                    unavailable_items=inventory.get_all_unavailable(),
                    overdue_items=inventory.get_all_overdue(),
                    MIN_DAYS=MIN_DAYS,
                    MAX_DAYS=MAX_DAYS,
                    MIN_LABELS=MIN_LABELS,
                    MAX_LABELS=MAX_LABELS, )

    @app.errorhandler(401)
    def unauthorized(_) -> flask.Response:
        logger.warning(f'Unauthorized access: {flask.request.url} from {flask.request.remote_addr}')
        return flask.redirect(flask.url_for('app.login'))

    @app.errorhandler(403)
    def unauthorized(_) -> flask.Response:
        flask.session.clear()
        logger.warning(f'Unauthorized access: {flask.request.url} from {flask.request.remote_addr}')
        return flask.redirect(flask.url_for('app.login'))

    @app.errorhandler(404)
    def page_not_found(_) -> str:
        return flask.render_template('404.html')

    @app.errorhandler(418)
    def teapot(_) -> flask.Response:
        return flask.redirect('https://www.youtube.com/watch?v=dQw4w9WgXcQ')

    return app


if __name__ == '__main__':
    init_db()
    create_app().run(host='0.0.0.0')

import os
from datetime import datetime
from urllib.parse import urlparse

import cachelib
import flask
from dateutil import parser
from flask_compress import Compress
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
from __init__ import logger, REGEX_ID, REGEX_ITEM, MIN_DAYS, MAX_DAYS, MIN_LABELS, MAX_LABELS, DEBUG, MOCK_DATA
from db import init_db, Settings
from routine_tasks import start_routine


def create_app() -> flask.Flask:
    # Flask app setup
    app = flask.Flask(__name__, template_folder='templates', static_folder='static')

    app.secret_key = os.getenv('SECRET_KEY')
    app.config['SESSION_TYPE'] = 'cachelib'
    app.config['SESSION_CACHELIB'] = cachelib.FileSystemCache(cache_dir='./flask_session', threshold=500)
    if os.getenv('DEBUG', 'false').lower() == 'true':
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
    def unauthorized_401(_) -> tuple[flask.Response, int]:
        flask.session.clear()
        if flask.request.url != flask.url_for('app.index', _external=True):
            logger.warning(f'Unauthorized access: {flask.request.url} from {flask.request.remote_addr}')
        return flask.redirect(flask.url_for('app.login')), 302

    @app.errorhandler(403)
    def unauthorized_403(_) -> tuple[flask.Response, int]:
        flask.session.clear()
        if flask.request.url != flask.url_for('app.index', _external=True):
            logger.warning(f'Unauthorized access: {flask.request.url} from {flask.request.remote_addr}')
        return flask.redirect(flask.url_for('app.login')), 302

    @app.errorhandler(404)
    def page_not_found(_) -> tuple[str, int]:
        return flask.render_template('404.html'), 404

    @app.errorhandler(418)
    def teapot(_) -> tuple[flask.Response, int]:
        return flask.redirect('https://www.youtube.com/watch?v=dQw4w9WgXcQ'), 302

    @app.errorhandler(500)
    def internal_server_error(_) -> tuple[str, int]:
        return flask.render_template('500.html'), 500

    @app.route('/robots.txt')
    def robots() -> flask.Response:
        return flask.send_from_directory(app.static_folder, 'robots.txt')

    @app.route('/service-worker.js')
    def service_worker() -> flask.Response:
        response = flask.make_response(flask.send_from_directory(app.static_folder, 'sw.js'))
        response.headers['Content-Type'] = 'application/javascript'
        return response

    # If we're in debug & mock-data mode, we can use /demo-login to skip logging in
    if DEBUG and MOCK_DATA:  # pragma: no cover
        @app.route('/demo-login')
        def debug_login() -> flask.Response:
            flask.session['user'] = user.User('demo', 'Demo User', '', ['admin'])
            return flask.redirect(flask.url_for('app.index'))

    app.config['COMPRESS_MIMETYPES'] = ['text/css', 'application/json', 'application/javascript']

    # Compress & minify
    Compress(app)
    Minify(app, static=False, go=False)  # Some static files don't minify well (breaks JS)

    init_db()
    Settings.verify_settings_exist()

    return app


# We need to create an app object for gunicorn to use with the routine tasks only running on the main thread, not the
# workers. But since gunicorn doesn't run on Windows we need to catch the exception and run the app normally
try:
    import gunicorn.app.base


    class App(gunicorn.app.base.BaseApplication):
        def __init__(self):
            start_routine()
            self.application = create_app()
            super().__init__()


    app = App()
except Exception as e:
    start_routine()
    app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0')

import flask

import inventory
from __init__ import KIOSK_FQDN, LABEL_SERVER
from db import add_admin, Settings
from sanitizer import handle_api_exception
from utils import login_required

app = flask.blueprints.Blueprint('app', __name__)


@app.route('/')
@login_required()
def index() -> str:
    if flask.session.get("user").is_admin:
        return flask.render_template('index_admin.html')
    return flask.render_template('index_student.html')


@app.route('/login')
def login() -> str | flask.Response:
    if flask.session.get("user"):
        return flask.redirect(flask.url_for('app.index'))
    if KIOSK_FQDN and flask.request.headers.get('Host') == KIOSK_FQDN:
        flask.session['method'] = 'kiosk'
        r = flask.request.referrer
        if r and r != flask.url_for('app.login'):
            return flask.redirect(r)
        return flask.redirect(flask.url_for('app.index'))
    return flask.render_template('login.html')


@app.route('/register')
@login_required()
def register() -> flask.Response:
    u = flask.session.get("user")
    if u.is_admin and not u.exists:
        add_admin(flask.session.get("user").__dict__)

    return flask.redirect(flask.url_for('app.index'))


@app.route('/logout')
def logout() -> flask.Response:
    flask.session.clear()
    return flask.redirect(flask.url_for('app.login'))


@app.route('/admin')
@login_required(admin_only=True)
def admin_settings() -> str:
    return flask.render_template('admin_settings.html', last_sent=Settings.get('report_last_sent') or 0,
                                 send_reports=Settings.get('send_reports') == '1')


@app.route('/audits')
@login_required(admin_only=True)
def audits() -> str:
    return flask.render_template('audits.html', search=flask.request.args.get('search'))


@app.route('/inventar')
@login_required(admin_only=True)
def inventar() -> str:
    return flask.render_template('inventar.html')


@app.route('/inventar/add')
@login_required(admin_only=True)
def inventar_add() -> str:
    return flask.render_template('inventar_add.html')


@app.route('/inventar/edit/<item_id>')
@login_required(admin_only=True)
@handle_api_exception
def edit_item(item_id: str) -> str:
    return flask.render_template('inventar_edit.html', item=inventory.get(item_id))


@app.route('/inventar/print/<item_id>')
@login_required(admin_only=True)
@handle_api_exception
def print_item(item_id: str) -> str:
    return flask.render_template('inventar_print.html', item=inventory.get(item_id))


@app.route('/booking')
@login_required(admin_only=True)
def booking() -> str:
    return flask.render_template('booking.html')


@app.route('/innlevering')
@login_required(admin_only=True)
def innlevering() -> str:
    """
    Renders the innlevering page.

    Parameters:
        warn (str): Whether to show the warning or not. Defaults to '1'.

    """

    return flask.render_template('innlevering.html',
                                 show_popup=False)  # show_popup=flask.request.args.get('show_popup', '1') == '1')


@app.route('/varetelling')
@login_required(admin_only=True)
def varetelling() -> str:
    return flask.render_template('varetelling.html')


@app.route('/registrer_avvik')
@login_required(admin_only=True)
def registrer_avvik() -> str:
    return flask.render_template('registrer_avvik.html')


@app.route('/etikettserver')
@login_required(admin_only=True)
def labelserver() -> str:  # pragma: no cover
    return flask.render_template('labelserver.html', labelserver_url=LABEL_SERVER)


@app.route('/ansvarsavtale')
def responsibility() -> str:
    return flask.render_template('responsibility.html')


@app.route('/personvern')
def privacy() -> str:
    return flask.render_template('privacy.html')

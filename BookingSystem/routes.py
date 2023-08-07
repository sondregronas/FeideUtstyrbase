import flask

import audits
import groups
import inventory
import mail
import user
from __init__ import KIOSK_FQDN
from __init__ import LABEL_SERVER
from db import add_admin
from utils import login_required

app = flask.blueprints.Blueprint('app', __name__)


@app.route('/')
@login_required()
def index() -> str:
    if flask.session.get("user").is_admin:
        return flask.render_template('index_admin.html', overdue_items=inventory.get_all_overdue())
    return flask.render_template('index_student.html', all_groups=groups.get_all())


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
    return flask.render_template('admin_settings.html', all_groups=groups.get_all(),
                                 all_categories=inventory.all_categories(),
                                 all_emails=mail.get_all_emails(),
                                 last_sent=mail.get_last_sent())


@app.route('/audits', endpoint='audits')
@login_required(admin_only=True)
def view_audits() -> str:
    return flask.render_template('audits.html', audits=audits.get_all())


@app.route('/inventar')
@login_required(admin_only=True)
def inventar() -> str:
    return flask.render_template('inventar.html', items=inventory.get_all())


@app.route('/inventar/add')
@login_required(admin_only=True)
def inventar_add() -> str:
    return flask.render_template('inventar_add.html', categories=inventory.all_categories())


@app.route('/inventar/edit/<item_id>')
@login_required(admin_only=True)
def edit_item(item_id: str) -> str:
    return flask.render_template('inventar_edit.html', item=inventory.get(item_id),
                                 categories=inventory.all_categories())


@app.route('/inventar/print/<item_id>')
@login_required(admin_only=True)
def print_item(item_id: str) -> str:
    return flask.render_template('inventar_print.html', item=inventory.get(item_id))


@app.route('/booking')
@login_required(admin_only=True)
def booking() -> str:
    return flask.render_template('booking.html',
                                 all_users=user.get_all_active_users(),
                                 all_items=inventory.get_all())


@app.route('/innlevering')
@login_required(admin_only=True)
def innlevering() -> str:
    return flask.render_template('innlevering.html',
                                 unavailable_items=inventory.get_all_unavailable())


@app.route('/etikettserver')
@login_required(admin_only=True)
def labelserver() -> str:
    return flask.render_template('labelserver.html', labelserver_url=LABEL_SERVER)


@app.route('/ansvarsavtale')
def responsibility() -> str:
    return flask.render_template('responsibility.html')


@app.route('/personvern')
def privacy() -> str:
    return flask.render_template('privacy.html')

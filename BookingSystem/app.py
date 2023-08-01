import flask
from dateutil import parser

import feide
import groups
from BookingSystem import app, logger, api, inventory, user
from BookingSystem.db import init_db, add_admin
from BookingSystem.utils import login_required

app.register_blueprint(api.api)
app.register_blueprint(feide.feide)
app.register_blueprint(groups.groups)


@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt='%d.%m.%Y') -> str:
    return parser.parse(date).strftime(fmt)


@app.errorhandler(401)
def unauthorized(e) -> flask.Response:
    logger.warning(f'Unauthorized access: {flask.request.url} from {flask.request.remote_addr}')
    return flask.redirect(flask.url_for('login'))


@app.route('/')
@login_required()
def index() -> str:
    if flask.session.get("user").is_admin:
        return flask.render_template('index_admin.html',
                                     overdue=inventory.get_all_overdue(),
                                     active=inventory.get_all_non_overdue())
    return flask.render_template('index_student.html', all_groups=groups.get_all())


@app.route('/login')
def login() -> str:
    return flask.render_template('login.html')


@app.route('/register')
@login_required()
def register() -> flask.Response:
    user = flask.session.get("user")
    if user.is_admin and not user.exists:
        add_admin(flask.session.get("user").__dict__)

    return flask.redirect(flask.url_for('index'))


@app.route('/logout')
@login_required()
def logout() -> flask.Response:
    flask.session.clear()
    return flask.redirect(flask.url_for('index'))


@app.route('/admin')
@login_required(admin_only=True)
def admin_settings() -> str:
    return flask.render_template('admin_settings.html', all_groups=groups.get_all(),
                                 all_categories=inventory.all_categories(),
                                 all_emails=groups.get_all_emails())


@app.route('/audits')
@login_required(admin_only=True)
def audits() -> str:
    """All audits in data/audits.log"""
    log = open('data/audits.log', 'r').readlines()
    log = [{
        'timestamp': audit.split('|')[0].strip(),
        'event': audit.split('|')[1].split(' - ')[0].strip(),
        'message': ''.join(audit.split(' - ')[1:]).strip()
    } for audit in log if audit.strip()]
    return flask.render_template('audits.html', audits=log)


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
@login_required()
def booking() -> str:
    return flask.render_template('booking.html',
                                 all_users=user.get_all_active_users(),
                                 all_items=inventory.get_all())


@app.route('/return')
@login_required()
def return_item() -> str:
    return flask.render_template('return.html')


if __name__ == '__main__':
    init_db()
    app.debug = True
    app.run(host='0.0.0.0')

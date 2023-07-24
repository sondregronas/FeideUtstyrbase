from logging import Logger, StreamHandler, Formatter

import flask
from flask_session import Session

# Global variables
DATABASE = 'db.sqlite'

# Flask app setup
app = flask.Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Logger setup
logger = Logger(__name__)
logger.setLevel('DEBUG')
logger.addHandler(StreamHandler())
logger.handlers[0].setFormatter(Formatter('[%(levelname)s | %(asctime)s]: %(message)s', '%Y-%m-%d %H:%M:%S'))

import os
from logging import Logger, StreamHandler, Formatter, FileHandler
from pathlib import Path

import flask
from dotenv import load_dotenv
from flask_session import Session

dotenv_path = Path('.env')
if dotenv_path.exists():
    load_dotenv(dotenv_path)

# Create data folder if it doesn't exist
Path('data').mkdir(exist_ok=True)

# Global variables
DATABASE = Path('data') / 'db.sqlite'
LABEL_SERVER = os.getenv('LABEL_SERVER')

# Flask app setup
app = flask.Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.getenv('SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Logger setup
logger = Logger(__name__)
logger.setLevel('DEBUG')
logger.addHandler(StreamHandler())
logger.handlers[0].setFormatter(Formatter('[%(levelname)s | %(asctime)s]: %(message)s', '%Y-%m-%d %H:%M:%S'))

audits = Logger('audits')
audits.setLevel('INFO')
audits.addHandler(FileHandler(Path('data') / 'audits.log'))
audits.handlers[0].setFormatter(Formatter('%(asctime)s | %(message)s', '%Y-%m-%d %H:%M:%S'))

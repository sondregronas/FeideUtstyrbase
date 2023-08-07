import os
from logging import Logger, StreamHandler, Formatter, FileHandler
from pathlib import Path

from dotenv import load_dotenv

dotenv_path = Path('.env')
if dotenv_path.exists():  # pragma: no cover
    load_dotenv(dotenv_path)

# Create data folder if it doesn't exist
Path('data').mkdir(exist_ok=True)

# Global variables
DATABASE = Path('data') / 'db.sqlite'
LABEL_SERVER = os.getenv('LABEL_SERVER')
KIOSK_FQDN = os.getenv('KIOSK_FQDN')
API_TOKEN = os.getenv('API_TOKEN')

# Logger setup
logger = Logger(__name__)
if os.getenv('DEBUG') == 'True':
    logger.setLevel('DEBUG')
else:
    logger.setLevel('INFO')
logger.addHandler(StreamHandler())
logger.handlers[0].setFormatter(Formatter('[%(levelname)s | %(asctime)s]: %(message)s', '%Y-%m-%d %H:%M:%S'))

audits = Logger('audits')
audits.setLevel('INFO')
audits.addHandler(FileHandler(Path('data') / 'audits.log'))
audits.handlers[0].setFormatter(Formatter('%(asctime)s | %(message)s', '%Y-%m-%d %H:%M:%S'))

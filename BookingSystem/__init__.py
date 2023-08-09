import os
from logging import Logger, StreamHandler, Formatter
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
REGEX_ITEM = r'^(?:(?![\s])[ÆØÅæøåa-zA-Z0-9_\s\-]*[ÆØÅæøåa-zA-Z0-9_\-]+)$'

MIN_DAYS = int(os.getenv('MIN_DAYS', 1))
MAX_DAYS = int(os.getenv('MAX_DAYS', 14))
MIN_LABELS = int(os.getenv('MIN_LABELS', 0))
MAX_LABELS = int(os.getenv('MAX_LABELS', 10))

# Logger setup
logger = Logger(__name__)
if os.getenv('DEBUG') == 'True':
    logger.setLevel('DEBUG')
else:
    logger.setLevel('INFO')
logger.addHandler(StreamHandler())
logger.handlers[0].setFormatter(Formatter('[%(levelname)s | %(asctime)s]: %(message)s', '%Y-%m-%d %H:%M:%S'))

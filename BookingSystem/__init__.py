import os
from logging import Logger, StreamHandler, Formatter
from pathlib import Path

from dotenv import load_dotenv

dotenv_path = Path(".env")
if dotenv_path.exists():  # pragma: no cover
    load_dotenv(dotenv_path)

# Create data folder if it doesn't exist
Path("data").mkdir(exist_ok=True)

# Global variables
DATABASE = Path("data") / "db.sqlite"
LABEL_SERVER = os.getenv("LABEL_SERVER")
KIOSK_FQDN = os.getenv("KIOSK_FQDN")
API_TOKEN = os.getenv("API_TOKEN")

# Teams webhooks
TEAMS_WEBHOOKS = os.getenv("TEAMS_WEBHOOKS")
TEAMS_WEBHOOKS_DEVIATIONS = os.getenv("TEAMS_WEBHOOKS_DEVIATIONS")
TEAMS_MSG_WEBHOOK = os.getenv("TEAMS_MSG_WEBHOOK")
if TEAMS_WEBHOOKS:
    TEAMS_WEBHOOKS = TEAMS_WEBHOOKS.split(",")
if TEAMS_WEBHOOKS_DEVIATIONS:
    TEAMS_WEBHOOKS_DEVIATIONS = TEAMS_WEBHOOKS_DEVIATIONS.split(",")

REGEX_ID = r"^(?:(?![\s])[a-zA-Z0-9_\s\-]*[a-zA-Z0-9_\-]+)$"
REGEX_ITEM = r"^(?:(?![\s])[ÆØÅæøåa-zA-Z0-9_\s\-]*[ÆØÅæøåa-zA-Z0-9_\-]+)$"

MIN_DAYS = int(os.getenv("MIN_DAYS", "1"))
MAX_DAYS = int(os.getenv("MAX_DAYS", "14"))
MIN_LABELS = int(os.getenv("MIN_LABELS", "0"))
MAX_LABELS = int(os.getenv("MAX_LABELS", "10"))

# Debugging / development / testing
DEBUG = os.getenv("DEBUG", "").lower() == "true"
MOCK_DATA = os.getenv("MOCK_DATA", "").lower() == "true"
if MOCK_DATA:  # pragma: no cover
    DATABASE = Path("data") / "mock_db.sqlite"

# Logger setup
logger = Logger(__name__)
logger.setLevel("DEBUG" if DEBUG else "INFO")
logger.addHandler(StreamHandler())
logger.handlers[0].setFormatter(
    Formatter("[%(levelname)s | %(asctime)s]: %(message)s", "%Y-%m-%d %H:%M:%S")
)

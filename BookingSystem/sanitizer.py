import re
from enum import Enum, auto
from functools import wraps

import flask

import groups
import inventory
from __init__ import REGEX_ITEM, logger, REGEX_ID


class VALIDATORS(Enum):
    ID = auto()
    UNIQUE_ID = auto()
    UNIQUE_OR_SAME_ID = auto()
    NAME = auto()
    CATEGORY = auto()
    CATEGORY_NAME = auto()
    INT = auto()
    LABEL_TYPE = auto()
    ITEM_LIST_EXISTS = auto()
    EMAIL = auto()
    GROUP = auto()
    GROUP_NAME = auto()


class APIException(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        logger.debug(f'APIException: {message}')


class MINMAX:
    def __init__(self, mn: int, mx: int):
        self.mn = mn
        self.mx = mx

    def __iter__(self):
        return iter((self.mn, self.mx))

    def __str__(self):
        return f'{self.mn}-{self.mx}'


def _sanitize_form(sanitization_map: dict[any: VALIDATORS | MINMAX], form, data: dict = dict) -> bool:
    """Sanitize a form based on a sanitization map."""
    def id_pattern(fkey: str) -> bool:
        # Check if the ID/name is valid
        r = re.compile(REGEX_ID)
        return bool(r.match(form.get(fkey)))

    def item_pattern(fkey: str) -> bool:
        # Check if the ID/name is valid
        r = re.compile(REGEX_ITEM)
        return bool(r.match(form.get(fkey)))

    def unique(fkey: str) -> bool:
        # Check if the ID is unique
        l_val, l_ids = form.get(fkey).lower(), [i.lower() for i in inventory.get_all_ids()]
        return l_val not in l_ids

    def email(text: str) -> bool:
        # Check if the email is valid
        r = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}$")
        return bool(r.match(text))

    def categoryname(text: str) -> bool:
        # Check if the category is valid
        r = re.compile(r'^[a-zæøåA-ZÆØÅ0-9\- ]+$')
        return bool(r.match(text))

    def groupname(text: str) -> bool:
        # Check if the group is valid
        r = re.compile(r'^([a-zæøåA-ZÆØÅ0-9\- ]+) \(([a-zæøåA-ZÆØÅ0-9\-& ]+)\)$')
        return bool(r.match(text))

    for key, sanitizer in sanitization_map.items():
        match sanitizer:
            case VALIDATORS.ID:
                if not id_pattern(key):
                    raise APIException(f'Ugyldig ID ({form.get(key)})')

            case VALIDATORS.NAME:
                # Check if the ID/name is valid
                if not item_pattern(key):
                    raise APIException(f'Ugyldig Navn ({form.get(key)})')

            case VALIDATORS.UNIQUE_ID:
                # Check if the ID is unique
                if not unique(key):
                    raise APIException(f'{form.get(key)} er allerede i bruk.')
                # Check if the ID is valid
                if not id_pattern(key):
                    raise APIException(f'Ugyldig ID ({form.get(key)})')

            case VALIDATORS.UNIQUE_OR_SAME_ID:
                # Check if the ID is unique or the same as the current ID
                same_id = form.get(key).lower() == data.get(key).lower()
                if not unique(key) and not same_id:
                    raise APIException(f'{form.get(key)} er allerede i bruk.')
                # Check if the ID is valid
                if not id_pattern(key):
                    raise APIException(f'Ugyldig ID ({form.get(key)})')

            case VALIDATORS.CATEGORY:
                # Check if the category is valid
                if form.get(key) not in inventory.all_categories():
                    raise APIException(f'Ugyldig kategori ({form.get(key)})')

            case VALIDATORS.CATEGORY_NAME:
                # Check if the category name is valid
                if not categoryname(form.get(key)):
                    raise APIException(f'Ugyldig kategorinavn ({form.get(key)})')

            case VALIDATORS.INT:
                # Check if the value is an int
                try:
                    int(form.get(key))
                except (ValueError, TypeError):
                    raise APIException(f'Ugyldig tallverdi ({form.get(key)})')

            case VALIDATORS.LABEL_TYPE:
                # Check if the label type is valid
                if form.get(key) not in ['barcode', 'qr']:
                    raise APIException(f'Ugyldig etikett-type ({form.get(key)})')

            case VALIDATORS.ITEM_LIST_EXISTS:
                # Check if the item list exists
                ids = form.getlist(key)
                all_ids = [i for i in inventory.get_all_ids()]
                if not all(i in all_ids for i in ids):
                    raise APIException(f'En eller flere gjenstander finnes ikke ({form.getlist(key)})')

            case VALIDATORS.EMAIL:
                # Check if the email is valid
                if not email(form.get(key)):
                    raise APIException(f'Ugyldig e-post ({form.get(key)})')

            case VALIDATORS.GROUP:
                # Check if the group is valid (done by students, send to 418 ;))
                if form.get(key) not in groups.get_all():
                    raise APIException(f'Ugyldig gruppe ({form.get(key)}), godt forsøk ;)', 418)

            case VALIDATORS.GROUP_NAME:
                # Check if the group name is valid
                if not groupname(form.get(key)):
                    raise APIException(f'Ugyldig gruppenavn ({form.get(key)}), må være "Klasserom (Lærer)"')

        if key.endswith('_minmax'):
            # Check if the value is between the min and max
            mn, mx = sanitizer
            if not mn <= int(form.get(key[:-7])) <= mx:
                logger.debug(f'Invalid minmax for {key} ({form.get(key)})')
                raise APIException(f'Tallverdien er ikke mellom {mn} og {mx} ({form.get(key)})')

        # Passed all checks!
        logger.debug(f'Validated {key} ({sanitizer}, {form.get(key)})')
    return True


def sanitize(validation_map: dict[any: VALIDATORS | MINMAX],
             form: dict,
             data: dict = dict) -> dict[str: any]:
    """
    Validate a form based on a validation map,
    return the same keys with form values if valid, else raise ValueError

    (Remove keys that end in _minmax from the returned dict)
    """
    try:
        _sanitize_form(validation_map, form, data)
        sanitized = dict()

        for key, sanitizer in validation_map.items():
            # Remove keys that are not in the validation map
            if key not in validation_map.keys():
                continue
            # Remove keys that end in _minmax
            if key.endswith('_minmax'):
                continue
            # Lists need to be handled as lists
            if sanitizer == VALIDATORS.ITEM_LIST_EXISTS:
                sanitized[key] = form.getlist(key)
                continue
            # Everything else can be handled as a single value
            sanitized[key] = form.get(key)

        logger.debug(f'Sanitized, old form: {form}')
        logger.debug(f'Sanitized, new form: {sanitized}')
        return sanitized
    except APIException as e:
        logger.warning(f'Invalid form submitted: {form}')
        raise APIException(e.message, e.status_code)


def handle_api_exception(f) -> callable:
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except APIException as e:
            return flask.Response(e.message, status=e.status_code)

    return wrapper

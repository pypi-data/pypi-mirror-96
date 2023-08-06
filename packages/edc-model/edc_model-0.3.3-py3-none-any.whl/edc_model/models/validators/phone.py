import re

from django.conf import settings
from django.core.exceptions import ValidationError


def phone_number(value, pattern=None):
    str_value = str(value)
    pattern = pattern or r"^[0-9+\(\)#\.\s\/ext-]+$"
    p = re.compile(pattern)
    if not p.match(str_value):
        raise ValidationError("Invalid format.")


def cell_number(value):
    try:
        pattern = settings.CELLPHONE_REGEX
    except AttributeError:
        pattern = None
    phone_number(value, pattern)


def telephone_number(value):
    try:
        pattern = settings.TELEPHONE_REGEX
    except AttributeError:
        pattern = None
    phone_number(value, pattern)

import re

from django.core.exceptions import ValidationError


def validate_national_id(national_id: str):
    if not re.match(r'^\d{10}$', national_id):
        raise ValidationError

    digits = [int(digit) for digit in national_id]
    s = 0
    for i in range(9):
        s += digits[i] * (10 - i)
    rem = s % 11
    if rem >= 2:
        rem = 11 - rem

    if digits[9] != rem:
        raise ValidationError

from random import choices
from string import digits

from reviews.constants import CONFIRMATION_CODE_LENGTH


def generate_confirmation_code():
    return ''.join(choices(digits, k=CONFIRMATION_CODE_LENGTH))

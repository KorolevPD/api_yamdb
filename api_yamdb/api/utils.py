from random import choices
from string import digits

from reviews.constants import CONFIRMATION_CODE_LENGTH


def generate_confirmation_code(code_length=CONFIRMATION_CODE_LENGTH):
    return ''.join(choices(digits, k=code_length))

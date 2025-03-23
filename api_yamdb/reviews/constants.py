EMAIL_MAX_LENGHT = 254

NAME_MAX_LENGHT = 256

SLUG_MAX_LENGHT = 50

TEXT_LEN = 30

USER_ROLES = (
    ('user', 'Обычный пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Админ'),
)

DEFAULT_USER_ROLE = 'user'


def get_roles_max_lenght():
    max_lenght = 0
    for role in USER_ROLES:
        max_lenght = max(len(role[0]), max_lenght)
    return max_lenght

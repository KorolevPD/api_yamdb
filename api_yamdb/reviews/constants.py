EMAIL_MAX_LENGHT = 254

NAME_MAX_LENGHT = 256

SLUG_MAX_LENGHT = 50

CONFIRMATION_CODE_LENGTH = 6

TEXT_LEN = 30

ADMIN_ROLE = 'admin'

MODERATOR_ROLE = 'moderator'

USER_ROLES = (
    ('user', 'Обычный пользователь'),
    (MODERATOR_ROLE, 'Модератор'),
    (ADMIN_ROLE, 'Админ'),
)

DEFAULT_USER_ROLE = 'user'


def get_roles_max_lenght():
    return max(len(role) for role, _ in USER_ROLES)

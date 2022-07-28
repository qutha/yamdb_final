from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail


def send_confirmation_code(user):
    """
    Метод отправляет email с кодом подтверждения при регистрации пользователя.
    """
    confirmation_code = default_token_generator.make_token(user)
    return send_mail(
        'Код подтверждения регистрации',
        f'{confirmation_code} - код регистрации',
        settings.ADMIN_EMAIL,
        [user.email]
    )

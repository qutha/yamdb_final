from django.contrib.auth.models import AbstractUser
from django.db import models

USER_ROLE, MODERATOR_ROLE, ADMIN_ROLE = 'user', 'moderator', 'admin'

CHOICES = (
    (USER_ROLE, 'Аутентифицированный пользователь'),
    (MODERATOR_ROLE, 'Модератор'),
    (ADMIN_ROLE, 'Администратор'),
)


class User(AbstractUser):
    """
    Добавление к стандартной модели User полей с биографией и ролью.
    """
    bio = models.TextField(verbose_name='Биография', blank=True)
    role = models.CharField(
        verbose_name='Роль',
        max_length=50,
        choices=CHOICES,
        default=USER_ROLE,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return f'{self.username} - {self.email}'

    @property
    def is_admin(self):
        return self.role == ADMIN_ROLE

    @property
    def is_moderator(self):
        return self.role == MODERATOR_ROLE

    @property
    def is_user(self):
        return self.role == USER_ROLE

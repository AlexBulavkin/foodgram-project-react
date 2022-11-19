from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import CheckConstraint, F, Q, UniqueConstraint


class User(AbstractUser):
    """Модель пользователя"""
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)
    USER = 'user'
    ADMIN = 'admin'

    ROLES = (
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
    )

    username = models.TextField('Пользователь',
                                unique=True,
                                max_length=150
                                )
    role = models.CharField('Роль',
                            max_length=10,
                            choices=ROLES,
                            default=USER)
    first_name = models.TextField('Имя',
                                  max_length=150)
    last_name = models.TextField('Фамилия',
                                 max_length=150)
    email = models.EmailField('E-mail',
                              unique=True,
                              max_length=254)

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """ Модель подписки на автора"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing'
    )

    def clean(self):
        if self.user == self.author:
            raise ValidationError('Вы не можете подписаться на самого себя.')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'],
                name='unique_author_user_subscribing'
            ),
            CheckConstraint(
                check=~Q(user=F('author')),
                name='self_following',
            ),
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}.'

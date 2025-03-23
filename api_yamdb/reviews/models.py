from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator
from django.db import models

from reviews.constants import (TEXT_LEN, USER_ROLES, DEFAULT_USER_ROLE,
                               SLUG_MAX_LENGHT, NAME_MAX_LENGHT,
                               get_roles_max_lenght)


class User(AbstractUser):
    bio = models.TextField(blank=True)
    role = models.CharField(
        choices=USER_ROLES,
        max_length=get_roles_max_lenght(),
        default=DEFAULT_USER_ROLE)
    confirmation_code = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def is_admin(self):
        return self.is_superuser or self.role == 'admin'

    def is_moderator(self):
        return self.is_admin() or self.role == 'moderator'


class Category(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGHT)
    slug = models.SlugField(max_length=SLUG_MAX_LENGHT, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGHT)
    slug = models.SlugField(max_length=SLUG_MAX_LENGHT, unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGHT)
    year = models.SmallIntegerField()
    description = models.TextField(null=True)
    genre = models.ManyToManyField(Genre)
    category = models.ForeignKey(
        Category, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Призведение'
        verbose_name_plural = 'Произведения'

    @property
    def rating(self):
        return self.reviews.aggregate(models.Avg('score'))['score__avg']


class Review(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              verbose_name='Название произведения')
    text = models.TextField(verbose_name='Текст отзыва')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор')
    score = models.PositiveIntegerField(validators=[MaxValueValidator(10)],
                                        verbose_name='Оценка')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = 'reviews'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_following'
            )
        ]

    def __str__(self):
        return self.text[:TEXT_LEN]


class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               verbose_name='Отзыв')
    text = models.TextField(verbose_name='Текст комментария')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'

    def __str__(self):
        return self.text[:TEXT_LEN]

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    bio = models.TextField()
    role = models.CharField(choices=settings.USER_ROLES, max_length=64)


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50)


class Genre(models.Model):
    pass


class Review(models.Model):
    pass


class Comment(models.Model):
    pass

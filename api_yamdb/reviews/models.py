from django.conf import settings
from django.core.validators import MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    bio = models.TextField()
    role = models.CharField(choices=settings.USER_ROLES, max_length=64)


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50)


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50)


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.IntegerField()
    description = models.TextField()
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Review(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(validators=[MaxValueValidator(10)])
    pub_date = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    pass

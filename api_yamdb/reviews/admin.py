from import_export.admin import ImportMixin
from django.contrib import admin

from .models import Comment, Review, Category, Genre, Title, User
from . import resources


@admin.register(Category)
class CategoryAdmin(ImportMixin, admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    resource_class = resources.CategoryResource


@admin.register(Comment)
class CommentAdmin(ImportMixin, admin.ModelAdmin):
    list_display = ("id", "review", "author", "pub_date")
    search_fields = ("review__title__name", "author__username")
    resource_class = resources.CommentResource


@admin.register(Genre)
class GenreAdmin(ImportMixin, admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    resource_class = resources.GenreResource


@admin.register(Review)
class ReviewAdmin(ImportMixin, admin.ModelAdmin):
    list_display = ("id", "title", "author", "score", "pub_date")
    search_fields = ("title__name", "author__username")
    list_filter = ("score", "pub_date")
    resource_class = resources.ReviewResource


@admin.register(Title)
class TitleAdmin(ImportMixin, admin.ModelAdmin):
    list_display = ("id", "name")
    resource_class = resources.TitleResource


@admin.register(User)
class UserAdmin(ImportMixin, admin.ModelAdmin):
    list_display = ("id", "username")
    resource_class = resources.UserResource

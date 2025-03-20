from django.contrib import admin

from reviews.models import Comment, Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "score", "pub_date")
    search_fields = ("title__name", "author__username")
    list_filter = ("score", "pub_date")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "review", "author", "pub_date")
    search_fields = ("review__title__name", "author__username")

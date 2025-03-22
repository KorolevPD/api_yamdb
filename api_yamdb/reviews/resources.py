from datetime import datetime

from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget, Widget

from .models import Category, Comment, Genre, Review, Title, User


class ISO8601DateWidget(Widget):

    def clean(self, value, **kwargs):
        if value:
            try:
                return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
            except ValueError:
                return None
        return value


class CategoryResource(resources.ModelResource):

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')


class CommentResource(resources.ModelResource):
    review_id = fields.Field(column_name='review_id', attribute='review',
                             widget=ForeignKeyWidget(Review, 'id'))
    pub_date = fields.Field(attribute='pub_date', column_name='pub_date',
                            widget=ISO8601DateWidget())

    class Meta:
        model = Comment
        fields = ('id', 'review_id', 'text', 'author', 'pub_date')


class GenreResource(resources.ModelResource):

    class Meta:
        model = Genre
        fields = ('id', 'name', 'slug')


class ReviewResource(resources.ModelResource):
    title_id = fields.Field(column_name='title_id', attribute='title',
                            widget=ForeignKeyWidget(Title, 'id'))

    pub_date = fields.Field(attribute='pub_date', column_name='pub_date',
                            widget=ISO8601DateWidget())

    class Meta:
        model = Review
        fields = ('id', 'title_id', 'text', 'author', 'score', 'pub_date')


class TitleResource(resources.ModelResource):

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'category')


class UserResource(resources.ModelResource):

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'bio', 'first_name',
                  'last_name')

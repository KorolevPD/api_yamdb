from rest_framework.validators import UniqueValidator
from rest_framework import serializers

from reviews.models import Review, User, Category, Genre, Comment, Title


class UserSerializer(serializers.ModelSerializer):
    email = serializers.CharField(
        allow_blank=False,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio',
                  'role')


class UserMeSerializer(UserSerializer):

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(
        validators=[UniqueValidator(queryset=Category.objects.all())]
    )

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(
        validators=[UniqueValidator(queryset=Genre.objects.all())]
    )

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):

    # TODO Добавить поле rating, которое высчитывается на основе отзывов
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), many=True, slug_field='slug', required=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug', required=True
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category', 'rating')

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Заменяем поле `category` на объект с полями `name` и `slug`
        category = representation.get('category')
        if category:
            category_instance = Category.objects.get(slug=category)
            representation['category'] = CategorySerializer(
                category_instance).data

        return representation

class SignupSerializer(UserSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', )
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('title',)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('review',)
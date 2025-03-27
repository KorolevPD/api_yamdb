from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from reviews.constants import EMAIL_MAX_LENGHT, SLUG_MAX_LENGHT
from reviews.models import Category, Comment, Genre, Review, Title, User
from .utils import generate_confirmation_code


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        max_length=EMAIL_MAX_LENGHT,
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
        max_length=SLUG_MAX_LENGHT,
        validators=[UniqueValidator(queryset=Category.objects.all())]
    )

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(
        max_length=SLUG_MAX_LENGHT,
        validators=[UniqueValidator(queryset=Genre.objects.all())]
    )

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.FloatField(read_only=True)
    genre = serializers.SlugRelatedField(
        many=True, queryset=Genre.objects.all(),
        slug_field='slug',
        allow_empty=False
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug', allow_empty=False
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category',
                  'rating')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['genre'] = GenreSerializer(
            instance.genre, many=True).data
        representation['category'] = CategorySerializer(instance.category).data
        return representation


class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=User._meta.get_field('username').max_length,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Имя пользователя может содержать только'
                'буквы, цифры и символы .@+-_'
            )
        ]
    )
    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        max_length=EMAIL_MAX_LENGHT
    )

    class Meta:
        model = User
        fields = ('username', 'email')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_email(self, value):
        if not value:
            raise ValidationError('Email обязателен')
        return value

    def validate_username(self, value):
        if not value:
            raise ValidationError('Невозможно создать пустое имя пользователя')
        if value.lower() == 'me':
            raise ValidationError('Невозможно создать никнейм "me"')
        return value

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')

        # Проверяем, существует ли пользователь с таким email
        user_by_email = User.objects.filter(email=email).first()
        if user_by_email:
            if user_by_email.username != username:
                raise serializers.ValidationError(
                    {'email': 'Этот email уже используется с другим username'}
                )

        # Проверяем, существует ли пользователь с таким username
        user_by_username = User.objects.filter(username=username).first()
        if user_by_username:
            if user_by_username.email != email:
                raise serializers.ValidationError(
                    {'username': 'Этот username уже занят другим email'}
                )

        return data

    def create(self, validated_data):
        user, created = User.objects.get_or_create(
            username=validated_data['username'],
            email=validated_data['email'],
            defaults={'is_active': True})

        if not created:
            user.is_active = False

        confirmation_code = generate_confirmation_code()
        user.confirmation_code = confirmation_code
        user.save()

        # Отправка email с кодом подтверждения
        send_mail(
            'Подтверждение регистрации',
            f'Ваш код подтверждения: {confirmation_code}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return user


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('title',)

    def create(self, validated_data):
        user = self.context['request'].user
        title = validated_data.get('title')

        if Review.objects.filter(title=title, author=user).exists():
            raise ValidationError('Вы уже оставили отзыв на это произведение.')

        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('review',)

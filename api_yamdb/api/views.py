from random import choices
from string import digits

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from permissions import (IsAdministrator, IsAuthorOrModeratorOrAdmin,
                         IsOwnerOrReadOnly)
from rest_framework import filters, mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Review, Title, User
from .filters import TitleFilter
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, SignupSerializer,
                          TitleSerializer, UserMeSerializer, UserSerializer)


class CreateListDestroyView(GenericViewSet, mixins.CreateModelMixin,
                            mixins.ListModelMixin, mixins.DestroyModelMixin):
    pass


class UserViewSet(ModelViewSet, mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsAdministrator)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    search_fields = ('username',)
    lookup_field = 'username'

    def update(self, request, *args, **kwargs):
        if not request.user.is_admin():
            handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)
        return super().update(request, *args, **kwargs)


class UserMeViewSet(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = UserMeSerializer(
            request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(CreateListDestroyView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated, IsAdministrator)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action == 'list':
            return (AllowAny(),)
        return super().get_permissions()


class GenreViewSet(CreateListDestroyView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAuthenticated, IsAdministrator)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action == 'list':
            return (AllowAny(),)
        return super().get_permissions()


class TitleViewSet(ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAuthenticated, IsAdministrator)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    lookup_field = 'id'

    def get_permissions(self):
        if self.action in ('retrieve', 'list'):
            return (AllowAny(),)
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT' or not request.user.is_admin():
            handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)
        return super().update(request, *args, **kwargs)


class UserSignupTokenViewSet(GenericViewSet):
    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = (AllowAny,)

    @action(detail=False, methods=['post'], url_path='signup')
    def signup(self, request):
        '''Регистрация пользователя или повторная отправка кода.'''
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        return Response({'username': user.username, 'email': user.email},
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='token')
    def token(self, request):
        '''Получение токена.'''
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')
        if not username or not confirmation_code:
            return Response(
                {'error': 'Username и confirmation_code обязательны'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Ищем пользователя по username; если не найден, генерируем ошибку 404
        user = get_object_or_404(User, username=username)
        if user.confirmation_code != confirmation_code:
            return Response({'error': 'Неверный код подтверждения'},
                            status=status.HTTP_400_BAD_REQUEST)
        user.is_active = True
        user.confirmation_code = ''
        try:
            user.save()
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }, status=status.HTTP_200_OK)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = (IsAuthenticated,
                                       IsAuthorOrModeratorOrAdmin)
        return super().get_permissions()

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs['title_pk'])

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        user = self.request.user
        if Review.objects.filter(title=self.get_title(), author=user).exists():
            raise ValidationError('Вы уже оставили отзыв на это произведение.')
        serializer.save(author=user, title=self.get_title())

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response({'detail': 'Метод PUT не разрешён.'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)


class CommentViewSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     GenericViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated,
                                       IsAuthorOrModeratorOrAdmin]
        return super().get_permissions()

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs['review_pk'])

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response({'detail': 'Метод PUT не разрешён.'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)

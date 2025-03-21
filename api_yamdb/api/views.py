from string import digits
from random import choices

from rest_framework import filters
from rest_framework import mixins
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly, )
from rest_framework.viewsets import (ModelViewSet, GenericViewSet)
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from reviews.models import Review, User, Category, Genre, Title
from permissions import (IsOwnerOrReadOnly, IsAuthorOrModeratorOrAdmin,
                         IsAdministrator)
from .serializers import (CategorySerializer, SignupSerializer, TitleSerializer,
                          ReviewSerializer, UserSerializer, GenreSerializer, CommentSerializer)


class UserViewSet(ModelViewSet, mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsAdministrator)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    http_method_names = ["get", "post", "patch", "delete"]
    search_fields = ('username',)
    lookup_field = 'username'

    def update(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.role == 'admin'):
            handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)
        return super().update(request, *args, **kwargs)


class UserMeViewSet(GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    @action(detail=True, methods=['get'], url_path='me')
    def get_me(self, request):
        pass

    @action(detail=True, methods=['patch'], url_path='me')
    def patch_me(self, request):
        pass


class CategoryViewSet(GenericViewSet, mixins.CreateModelMixin,
                      mixins.ListModelMixin, mixins.DestroyModelMixin):
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


class GenreViewSet(GenericViewSet, mixins.CreateModelMixin,
                   mixins.ListModelMixin, mixins.DestroyModelMixin):
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
    lookup_field = 'id'

    # TODO Нужно объединить дублирующийся код с CategoryViewSet и GenreViewSet
    # в отдельный пермишен
    def get_permissions(self):
        if self.action in ('retrieve', 'list'):
            return (AllowAny(),)
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)


class UserSignupTokenViewSet(GenericViewSet):
    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = (AllowAny,)

    def generate_confirmation_code(self, length=6):
        # Генерирует случайный числовой код длиной 6 символов.
        return ''.join(choices(digits, k=length))

    @action(detail=False, methods=['post'], url_path='signup')
    def signup(self, request):
        """Регистрация пользователя."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(is_active=False)
            confirmation_code = self.generate_confirmation_code()
            user.confirmation_code = confirmation_code
            user.save()

            send_mail(
                'Подтверждение регистрации',
                f'Ваш код подтверждения: {confirmation_code}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            return Response(
                {'message': 'Письмо с кодом подтверждения отправлено.'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='token')
    def token(self, request):
        """Получение токена."""
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
        # Если код верный, активируем пользователя
        user.is_active = True
        user.confirmation_code = ''
        try:
            user.save()
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # Генерируем JWT-токены
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
            self.permission_classes = [IsAuthorOrModeratorOrAdmin]
        return super().get_permissions()

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs['title_pk'])

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        user = self.request.user
        if Review.objects.filter(title=self.get_title(), author=user).exists():
            raise ValidationError("Вы уже оставили отзыв на это произведение.")
        serializer.save(author=user, title=self.get_title())

    def update(self, request, *args, **kwargs):
        if request.method == "PUT":
            return Response({"detail": "Метод PUT не разрешён."},
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
            self.permission_classes = [IsAuthorOrModeratorOrAdmin]
        return super().get_permissions()

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs['review_pk'])

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())

    def update(self, request, *args, **kwargs):
        if request.method == "PUT":
            return Response({"detail": "Метод PUT не разрешён."},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)

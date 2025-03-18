import random
import string
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import SignupSerializer, UserProfileSerializer
from permissions import IsOwnerOrReadOnly
from reviews.models import Review
from api.serializers import ReviewSerializer


User = get_user_model()

def generate_confirmation_code(length=6):
    # Генерирует случайный числовой код длиной 6 символов.
    return ''.join(random.choices(string.digits, k=length))


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = SignupSerializer

    @action(detail=False, methods=['post'], url_path='auth/signup')
    def signup(self, request):
        """Регистрация пользователя."""
        # Создаем экземпляр сериализатора с данными из запроса
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(is_active=False)
            confirmation_code = generate_confirmation_code()
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
    
    @action(detail=False, methods=['post'], url_path='auth/token')
    def token(self, request):
        """Получение токена."""
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')
        if not username or not confirmation_code:
            return Response({'error': 'Username и confirmation_code обязательны'}, status=status.HTTP_400_BAD_REQUEST)
        # Ищем пользователя по username; если не найден, генерируем ошибку 404
        user = get_object_or_404(User, username=username)
        if user.confirmation_code != confirmation_code:
            return Response({'error': 'Неверный код подтверждения'}, status=status.HTTP_400_BAD_REQUEST)
        # Если код верный, активируем пользователя
        user.is_active = True
        user.confirmation_code = ''
        try:
            user.save()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # Генерируем JWT-токены
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }, status=status.HTTP_200_OK)


class UserProfileViewSet(viewsets.GenericViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def partial_update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_title(self):
        return get_object_or_404(Review, pk=self.kwargs['title_id'])

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())

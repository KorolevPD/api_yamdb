from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import UserSignupTokenViewSet, UserViewSet


router = SimpleRouter()
router.register(r'auth', UserSignupTokenViewSet, 'users')

# TODO Нужно объединить эти эндпоинты
router.register(r'users', UserViewSet, 'users')
router.register(r'users/me', UserViewSet, 'user-profile')

urlpatterns = [
    path('v1/', include(router.urls)),
]

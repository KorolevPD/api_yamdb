from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import UserSignupTokenViewSet, UserViewSet, ReviewViewSet

router = SimpleRouter()
router.register(r'auth', UserSignupTokenViewSet, 'users')

# TODO Нужно объединить эти эндпоинты
router.register(r'users', UserViewSet, 'users')
router.register(r'users/me', UserViewSet, 'user-profile')
router.register(r'titles/(?P<title_pk>\d+)/reviews', ReviewViewSet, basename='reviews')

urlpatterns = [
    path('v1/', include(router.urls)),
]

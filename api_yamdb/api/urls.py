from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import UserProfileViewSet, UserViewSet


router = SimpleRouter()
router.register(r'users', UserViewSet, 'users')
router.register(r'users/me', UserProfileViewSet, 'user-profile')

urlpatterns = [
    path('v1/', include(router.urls)),
]

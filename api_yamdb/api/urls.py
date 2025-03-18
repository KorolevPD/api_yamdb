from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, UserProfileViewSet

v1_router = DefaultRouter()
v1_router.register(r'users', UserViewSet, basename='users')
v1_router.register(r'users/me', UserProfileViewSet, basename='user-profile')

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('v1/', include('djoser.urls.jwt')),
]
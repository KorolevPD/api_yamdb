from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (UserSignupTokenViewSet, UserViewSet, ReviewViewSet,
                    CategoryViewSet, GenreViewSet, CommentViewSet)


router = SimpleRouter()
router.register(r'auth', UserSignupTokenViewSet, 'auth')
router.register(r'users', UserViewSet, 'users')
router.register(r'categories', CategoryViewSet, 'categories')
router.register(r'genres', GenreViewSet, 'genres')
router.register(r'titles/(?P<title_pk>\d+)/reviews', ReviewViewSet,
                basename='reviews')
router.register(r'titles/(?P<title_pk>\d+)/reviews/(?P<review_pk>\d+)/comments', CommentViewSet, 'comments')

urlpatterns = [
    path('v1/', include(router.urls)),
]

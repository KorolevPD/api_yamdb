from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register(r'auth', views.UserSignupTokenViewSet, 'auth')
router.register(r'users', views.UserViewSet, 'users')
router.register(r'categories', views.CategoryViewSet, 'categories')
router.register(r'genres', views.GenreViewSet, 'genres')
router.register(r'titles', views.TitleViewSet, 'titles')
router.register(r'titles/(?P<title_pk>\d+)/reviews', views.ReviewViewSet,
                basename='reviews')
router.register(
    r'titles/(?P<title_pk>\d+)/reviews/(?P<review_pk>\d+)/comments',
    views.CommentViewSet,
    'comments')

urlpatterns = [
    path('v1/', include(router.urls)),
]

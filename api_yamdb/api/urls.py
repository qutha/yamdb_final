from django.urls import include, path
from rest_framework import routers

from .views import (
    CategoryViewSet, CommentViewSet, GenreViewSet, ReviewViewSet, TitleViewSet,
    UserViewSet, code_reset, signup, token,
)

app_name = 'api'

router = routers.DefaultRouter()

router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')
router.register('titles', TitleViewSet, basename='titles')
router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments'
)
router.register('users', UserViewSet, basename='users')

auth_urls = [
    path('signup/', signup, name='signup'),
    path('token/', token, name='token'),
    path('reset/', code_reset, name='reset'),
]

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/', include(auth_urls)),
]

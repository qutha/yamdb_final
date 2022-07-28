from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, mixins, viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.filters import TitleFilter
from reviews.models import Category, Genre, Title, Review
from users.models import User
from .permissions import IsAdminRole, IsModeratorRole, IsAuthor
from .serializers import (
    CategorySerializer, GenreSerializer, TitleSerializer, ReviewSerializer,
    CommentSerializer, TitleReadSerializer,
    UserSerializer, RegisterUserSerializer, AccessTokenSerializer,
    CodeResetSerializer,
)
from .services import send_confirmation_code


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Доступные эндпоинты:
    /titles/{title_id}/reviews/ - GET, POST;
    /titles/{title_id}/reviews/{review_id}/ - GET, PATCH, DELETE.
    """
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminRole | IsModeratorRole | IsAuthor,)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Доступные эндпоинты:
    /titles/{title_id}/reviews/{review_id}/comments/ - GET, POST;
    /titles/{title_id}/reviews/{review_id}/comments/{comment_id}/ - GET,
    PATCH, DELETE.
    """
    serializer_class = CommentSerializer
    permission_classes = (IsAdminRole | IsModeratorRole | IsAuthor,)

    def get_queryset(self):
        review = get_object_or_404(
            Review, title__id=self.kwargs.get('title_id'),
            pk=self.kwargs.get('review_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review, title__id=self.kwargs.get('title_id'),
            pk=self.kwargs.get('review_id')
        )
        serializer.save(author=self.request.user, review=review)


class TitleViewSet(viewsets.ModelViewSet):
    """
    Доступные эндпоинты:
    /titles/ - GET, POST;
    /titles/{titles_id}/ - GET, PATCH, DELETE.
    Фильтрация по полям - name, genre, category, year.
    """
    queryset = Title.objects.all()
    serializer_class = TitleReadSerializer
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_queryset(self):
        return (
            Title.objects.annotate(rating=Avg('reviews__score')).order_by('id')
        )

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return TitleReadSerializer
        return TitleSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (AllowAny(),)
        return (IsAdminRole(),)


class ListCreateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    pass


class CategoryViewSet(ListCreateDestroyViewSet):
    """
    Доступные эндпоинты
    /categories/ - GET, POST;
    /categories/{slug}/ - DELETE.
    Поиск по полю - name.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (AllowAny(),)
        return (IsAdminRole(),)


class GenreViewSet(ListCreateDestroyViewSet):
    """
    Доступные эндпоинты
    /genres/ - GET, POST;
    /genres/{slug}/ - DELETE.
    Поиск по полю - name.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (AllowAny(),)
        return (IsAdminRole(),)


class UserViewSet(viewsets.ModelViewSet):
    """
    Доступны эндпоинты
    /users/ - GET, POST;
    /users/{username}/ - GET, PATCH, DELETE.
    Поиск по полю - username.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'username'
    permission_classes = (IsAdminRole, )
    search_fields = ('username',)

    @action(
        detail=False, url_path='me', methods=['GET', 'PATCH'],
        permission_classes=(IsAuthenticated,),
    )
    def current_user(self, request):
        """
        Дополнительный эндпоинт:
        /users/me/ - GET, PATCH;
        Просмотр и редактирование собственного профиля.
        """
        user = get_object_or_404(User, pk=request.user.pk)
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(
            user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """
    Эндпоинт:
    /auth/signup/ - POST;
    Регистрация пользователя.
    """
    serializer = RegisterUserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        """Сбросить код на строке 227"""
        send_confirmation_code(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def token(request):
    """
    Эндпоинт:
    /auth/token/ - POST;
    Получить токен для аутентификации.
    """
    serializer = AccessTokenSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    username = serializer.data['username']
    user = get_object_or_404(User, username=username)
    confirmation_code = serializer.data['confirmation_code']
    if not default_token_generator.check_token(user, confirmation_code):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    access_token = RefreshToken.for_user(user)
    return Response(
        {'token': str(access_token.access_token)}, status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def code_reset(request):
    """
    Эндпоинт:
    /auth/reset/ - POST;
    Отправить код аутентификации повторно.
    """
    serializer = CodeResetSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.data['username']
        email = serializer.data['email']
        user = get_object_or_404(User, username=username, email=email)
        send_confirmation_code(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

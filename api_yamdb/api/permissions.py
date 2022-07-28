from rest_framework import permissions


class IsAdminRole(permissions.BasePermission):
    """Права для пользователя с ролью admin."""
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.is_admin or user.is_superuser

    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.is_authenticated and user.is_admin or user.is_superuser


class IsModeratorRole(permissions.BasePermission):
    """Права для пользователя с ролью moderator."""
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.is_moderator

    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.is_authenticated and user.is_moderator


class IsAuthor(permissions.BasePermission):
    """Права для автора записи."""
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user == obj.author
        )

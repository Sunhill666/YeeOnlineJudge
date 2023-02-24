from rest_framework import permissions

from organization.models import User


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_staff or request.user.is_superuser))


class HasPermissionOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in permissions.SAFE_METHODS or
            request.user.user_permission == User.Permission.ALL or
            (request.user.user_permission == User.Permission.SELF and
             obj.created_by == request.user)
        )

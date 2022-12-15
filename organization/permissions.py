from rest_framework import permissions

from organization.models import User


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)


class HasPermissionOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.user_permission == User.Permission.ALL:
            return True
        elif request.user.user_permission == User.Permission.SELF and obj.created_by == request.user:
            return True
        return False


class HasPermissionToJoin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        pass

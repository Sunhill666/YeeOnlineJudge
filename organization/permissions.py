from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated, IsAuthenticatedOrReadOnly, \
    SAFE_METHODS

from organization.models import User
from training.models import Training


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_staff or request.user.is_superuser))


class HasPermissionOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS or
            request.user.user_permission == User.Permission.ALL or
            (request.user.user_permission == User.Permission.SELF and
             obj.created_by == request.user)
        )


class CanJoinTraining(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        user_group = request.user.profile.group
        train_user = obj.user
        train_group = obj.group
        return bool(
            (train_user.count() == 0 and train_group.count() == 0) or
            (train_user.contains(user) or 
            train_group.contains(user_group) or
            user_group.name == "管理组")
        )


class CanSubmit(BasePermission):
    def has_permission(self, request, view):
        if training := request.data.get('training'):
            train_user = Training.objects.get(pk=training).user
            train_group = Training.objects.get(pk=training).group
            user = request.user
            user_group = request.user.profile.group
            return bool(
                (train_user.count() == 0 and train_group.count() == 0) or
                (train_user.contains(user) or 
                train_group.contains(user_group) or
                user_group.name == "管理组")
            )
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated
        )

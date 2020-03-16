import rest_framework as drf
from rest_framework.permissions import BasePermission


class SelfOnly(BasePermission):
    def has_permission(self, request, view):
        if not request.user:
            return False
        if request.user.is_staff:
            return True
        return hasattr(request.user, 'nickname') and request.user.nickname == view.kwargs['nickname']


class AllReadOwnerWrites(BasePermission):
    def has_permission(self, request, view):
        if request.method in drf.permissions.SAFE_METHODS:
            return True
        if not request.user:
            return False
        if request.user.is_staff:
            return True
        return hasattr(request.user, 'nickname') and request.user.nickname == view.kwargs['nickname']
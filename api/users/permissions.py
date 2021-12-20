from rest_framework import permissions

from .models import User


class UpdateStatsPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = User.objects.filter(username=request.user.username).first()
        if user:
            return user.is_admin


class ParsTrendsPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = User.objects.filter(username=request.user.username).first()
        if user:
            return user.is_admin

from django.http.request import HttpRequest

from rest_framework.permissions import BasePermission


class IsVerified(BasePermission):

    def has_permission(self, request: HttpRequest, view):
        return bool(request.user and request.user.is_authenticated and request.user.verified)

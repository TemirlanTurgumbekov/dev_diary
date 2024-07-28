from rest_framework import permissions
from .models import Article

class IsAuthor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'author'
    

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            if obj.status == Article.PUBLIC:
                return True
            if request.user.is_authenticated and request.user.role == 'subscriber':
                return True
        return obj.author == request.user

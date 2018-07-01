from django.contrib.auth.models import User
from rest_framework.permissions import BasePermission

from notes.models import Note, Notebook


class AuthorizedUsersPermission(BasePermission):

    def has_permission(self, request, view):
        """
        Allows access to pages only to authenticated users.
        """
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Allows access to models only to authenticated users.
        """
        return request.user and request.user.is_authenticated


class NotePermission(AuthorizedUsersPermission):

    def has_object_permission(self, request, view, obj):
        """
        Allows access to notes only to their owners.
        """
        if isinstance(obj, Note):
            return super().has_permission(request, view) and obj.notebook.owner.username == request.user.username
        return False


class NotebookPermission(AuthorizedUsersPermission):

    def has_object_permission(self, request, view, obj):
        """
        Allows access to notebooks only to their owners.
        """
        if isinstance(obj, Notebook):
            return super().has_permission(request, view) and obj.owner.username == request.user.username
        return False


class UserPermission(AuthorizedUsersPermission):

    def has_object_permission(self, request, view, obj):
        """
        Allows access to users only to their owners.
        """
        if isinstance(obj, User):
            return super().has_permission(request, view) and obj.username == request.user.username
        return False

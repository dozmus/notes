from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.reverse import reverse

from api.permissions import NotePermission, NotebookPermission, UserPermission
from api.serializers import NoteSerializer, UserSerializer, NotebookSerializer
from notes.models import Note, Notebook


@api_view(['GET'])
def root_view(request, format=None):
    return Response({
        'notes': reverse('api:note-list', request=request, format=format),
        'notebooks': reverse('api:notebook-list', request=request, format=format),
        'users': reverse('api:user-list', request=request, format=format),
    })


class NoteList(ListCreateAPIView):
    """
    List all notes, or create a new note.
    """
    serializer_class = NoteSerializer
    permission_classes = (NotePermission, )

    def get_queryset(self):
        return Note.objects.filter(notebook__owner=self.request.user)


class NoteDetail(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a note instance.
    """
    serializer_class = NoteSerializer
    permission_classes = (NotePermission, )

    def get_queryset(self):
        return Note.objects.filter(notebook__owner=self.request.user)


class NotebookList(ListCreateAPIView):
    """
    List all notebooks, or create a new note.
    """
    serializer_class = NotebookSerializer
    permission_classes = (NotebookPermission, )

    def get_queryset(self):
        return Notebook.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class NotebookDetail(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a notebook instance.
    """
    serializer_class = NotebookSerializer
    permission_classes = (NotebookPermission, )

    def get_queryset(self):
        return Notebook.objects.filter(owner=self.request.user)


class UserList(ListAPIView):
    """
    List all users.
    """
    serializer_class = UserSerializer
    permission_classes = (UserPermission, )

    def get_queryset(self):
        return User.objects.filter(username=self.request.user.username)


class UserDetail(RetrieveAPIView):
    """
    Retrieve a user instance.
    """
    serializer_class = UserSerializer
    permission_classes = (UserPermission, )

    def get_queryset(self):
        return User.objects.filter(username=self.request.user.username)

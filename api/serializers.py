from django.contrib.auth.models import User
from rest_framework.fields import ReadOnlyField
from rest_framework.relations import HyperlinkedRelatedField
from rest_framework.serializers import ModelSerializer

from notes.models import Note, Notebook


class NoteSerializer(ModelSerializer):
    class Meta:
        model = Note
        fields = ('id', 'title', 'content', 'notebook', 'trash', 'tags', )


class NotebookSerializer(ModelSerializer):
    owner = ReadOnlyField(source='owner.username')
    notes = HyperlinkedRelatedField(many=True, read_only=True, view_name='api:note-detail')

    class Meta:
        model = Notebook
        fields = ('id', 'title', 'colour', 'owner', 'notes', )


class UserSerializer(ModelSerializer):
    notebooks = HyperlinkedRelatedField(many=True, read_only=True, view_name='api:notebook-detail')

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'notebooks', )

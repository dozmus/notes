from django.forms import ModelForm

from .models import Note, Notebook


class NotebookForm(ModelForm):
    class Meta:
        model = Notebook
        fields = ['title']


class NoteForm(ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content', 'notebook']

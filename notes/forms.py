from django import forms

from .models import Note, Notebook


class NotebookForm(forms.ModelForm):
    class Meta:
        model = Notebook
        fields = ['title']


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content', 'notebook']

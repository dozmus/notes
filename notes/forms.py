from django.forms import ModelForm

from .models import Note, Notebook


class NotebookForm(ModelForm):
    class Meta:
        model = Notebook
        fields = ['title']


class NoteForm(ModelForm):
    def restrict_to_user(self, user):
        self.fields['notebook'].queryset = Notebook.objects.filter(owner=user)

    class Meta:
        model = Note
        fields = ['title', 'content', 'notebook']

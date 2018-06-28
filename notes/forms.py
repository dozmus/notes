from django.forms import ModelForm, Form, MultipleChoiceField, CheckboxSelectMultiple

from .models import Note, Notebook, UserProfile


class NotebookForm(ModelForm):
    class Meta:
        model = Notebook
        fields = ['title', 'colour']


class NoteForm(ModelForm):
    def restrict_to_user(self, user):
        self.fields['notebook'].queryset = Notebook.objects.filter(owner=user)

    class Meta:
        model = Note
        fields = ['title', 'content', 'notebook', 'tags']


class SelectNotebookForm(ModelForm):
    def restrict_to_user(self, user):
        self.fields['notebook'].queryset = Notebook.objects.filter(owner=user)

    class Meta:
        model = Note
        fields = ['notebook']


class SelectNotesForm(Form):
    def set_choices(self, notes):
        choices = tuple([(note.id, str(note)) for note in notes])
        lbl = 'Select some notes to interact with.'
        widget = CheckboxSelectMultiple()
        self.fields['picked'] = MultipleChoiceField(label=lbl, choices=choices, widget=widget, required=False)


class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['compact_mode', 'theme', 'syntax_highlighting_style']

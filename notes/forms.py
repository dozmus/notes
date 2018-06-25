from django.forms import ModelForm, Form, MultipleChoiceField, CheckboxSelectMultiple

from .models import Note, Notebook, UserProfile, SharableLink


class NotebookForm(ModelForm):
    class Meta:
        model = Notebook
        fields = ['title', 'colour']


class NoteForm(ModelForm):
    def restrict_to_user(self, user):
        self.fields['notebook'].queryset = Notebook.objects.filter(owner=user)

    class Meta:
        model = Note
        fields = ['title', 'content', 'notebook']


class SharedNoteForm(ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content']


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
        self.fields['picked'] = MultipleChoiceField(label=lbl, choices=choices, widget=CheckboxSelectMultiple(), required=False)


class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['syntax_highlighting_style']


class SharableLinkForm(ModelForm):
    def set_code(self, code):
        self.fields['code'].widget.attrs['value'] = code
        self.fields['code'].widget.attrs['readonly'] = True

    class Meta:
        model = SharableLink
        fields = ['code', 'permissions', 'expiry_date']


class EditSharableLinkForm(ModelForm):
    class Meta:
        model = SharableLink
        fields = ['permissions', 'expiry_date']

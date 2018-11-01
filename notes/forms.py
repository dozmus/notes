from django.forms import ModelForm, Form, MultipleChoiceField, CheckboxSelectMultiple

from .models import Note, Notebook, UserProfile


class NotebookForm(ModelForm):
    def create(self, user):
        if self.is_valid():
            notebook = self.save(commit=False)
            notebook.owner = user
            notebook.save()
            return True
        return False

    def update(self, notebook):
        if self.is_valid():
            notebook.title = self.cleaned_data['title']
            notebook.colour = self.cleaned_data['colour']
            notebook.save()
            return True
        return False

    class Meta:
        model = Notebook
        fields = ['title', 'colour']


class NoteForm(ModelForm):
    def create(self):
        if self.is_valid():
            self.save()
            return True
        return False

    def update(self):
        if self.is_valid():
            self.save()
            return True
        return False

    def update(self, note=None):
        if self.is_valid():
            note.title = self.cleaned_data['title']
            note.notebook = self.cleaned_data['notebook']
            note.content = self.cleaned_data['content']
            note.tags = self.cleaned_data['tags']
            note.save()
            return True
        return False

    def restrict_to_user(self, user):
        self.fields['notebook'].queryset = Notebook.objects.filter(owner=user)

    class Meta:
        model = Note
        fields = ['title', 'content', 'notebook', 'tags']


class SelectNotebookForm(ModelForm):
    def move(self, notes):
        if self.is_valid():
            for note in notes:
                note.notebook = self.cleaned_data['notebook']
                note.save()
            return True
        return False

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
    def update(self, profile):
        if self.is_valid():
            profile.theme = self.cleaned_data['theme']
            profile.syntax_highlighting_style = self.cleaned_data['syntax_highlighting_style']
            profile.compact_mode = self.cleaned_data['compact_mode']
            profile.save()
            return True
        return False

    class Meta:
        model = UserProfile
        fields = ['compact_mode', 'theme', 'syntax_highlighting_style']

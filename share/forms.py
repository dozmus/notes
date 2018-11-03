from django.forms import ModelForm

from notes.models import Note
from notes.task_lists import compute_task_counts
from share.models import SharableLink


class SharedNoteForm(ModelForm):
    def update(self, note, sharable_link):
        if self.is_valid() and sharable_link.permissions == 'read+write':
            note.title = self.cleaned_data['title']
            note.content = self.cleaned_data['content']
            note.tags = self.cleaned_data['tags']

            complete_tasks, total_tasks = compute_task_counts(note.content)
            note.complete_tasks = complete_tasks
            note.total_tasks = total_tasks
            note.save()
            return True
        return False

    class Meta:
        model = Note
        fields = ['title', 'content', 'tags']


class SharableLinkForm(ModelForm):
    def create(self, note_id):
        if self.is_valid():
            SharableLink.objects.create(note_id=note_id,
                                        code=self.cleaned_data['code'],
                                        permissions=self.cleaned_data['permissions'],
                                        expiry_date=self.cleaned_data['expiry_date'])
            return True
        return False

    def set_code(self, code):
        self.fields['code'].widget.attrs['value'] = code
        self.fields['code'].widget.attrs['readonly'] = True

    class Meta:
        model = SharableLink
        fields = ['code', 'permissions', 'expiry_date']


class EditSharableLinkForm(ModelForm):
    def update(self, link):
        if self.is_valid():
            link.permissions = self.cleaned_data['permissions']
            link.expiry_date = self.cleaned_data['expiry_date']
            link.save()
            return True
        return False

    class Meta:
        model = SharableLink
        fields = ['permissions', 'expiry_date']

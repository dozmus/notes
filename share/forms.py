from django.forms import ModelForm
from django.forms.utils import ErrorList

from notes.models import Note
from share.models import SharableLink


class SharedNoteForm(ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content', 'tags']


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

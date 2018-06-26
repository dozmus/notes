from colorful.fields import RGBColorField
from django.contrib.auth.models import User
from django.db.models import Model, CharField, TextField, ForeignKey, CASCADE
from django.forms import Textarea

from notes.syntax_highlighting import SYNTAX_HIGHLIGHTING_CHOICES
from notes.themes import THEME_CHOICES


class TagsInput(Textarea):
    template_name = 'tags/widgets/tagsinput.html'

    def __init__(self, attrs=None, tagify_settings=None):
        """
        :param tagify_settings: Various settings used to configure Tagify.
        You can specify if 'duplicates' are allowed (boolean).
        You can specify 'autocomplete' (boolean) - this matches from the whitelist.
        You can specify 'enforceWhitelist' (boolean).
        You can specify 'maxTags' (int).
        You can specify the 'whitelist' (string list).
        You can specify the 'blacklist' (string list).
        You can specify the 'delimiters' (string).
        You can specify the RegEx 'pattern' to validate the input (string).
        """
        # TODO validate settings
        super().__init__(attrs)
        self.tagify_settings = tagify_settings or {}

    def get_context(self, name, value, attrs):
        ctx = super().get_context(name, value, attrs)

        if 'tagify_settings' not in ctx:
            ctx['tagify_settings'] = self.tagify_settings
        return ctx

    class Media:
        js = ('js/tagify.js', 'js/tagify.polyfills.js', 'js/jQuery.tagify.min.js')
        css = {'all': ('css/tagify.css', )}


class TagsField(CharField):
    description = 'Tags'

    def __init__(self, widget_settings=None, *args, **kwargs):
        self.widget_settings = widget_settings or {}
        defaults = {
            'help_text': 'Press enter or comma after each tag you define.',
        }
        defaults.update(kwargs)
        super(TagsField, self).__init__(*args, **defaults)

    def to_python(self, value):
        if value is None or value == '':
            return value

        # value from the TagsInput are en-quoted and comma-separated
        value = value.lstrip('"')
        value = value.rstrip('"')
        value = value.replace('","', ',')
        return value

    def formfield(self, **kwargs):
        kwargs['widget'] = TagsInput({'class': 'form-control'}, self.widget_settings)
        return super(TagsField, self).formfield(**kwargs)


class Notebook(Model):
    title = CharField(max_length=100)
    colour = RGBColorField()
    owner = ForeignKey(User, on_delete=CASCADE)

    class Meta:
        verbose_name_plural = 'notebooks'

    def __str__(self):
        return self.title + ' (id=' + str(self.id) + ')'


class Note(Model):
    title = CharField(max_length=100)
    content = TextField(max_length=1000)
    notebook = ForeignKey(Notebook, on_delete=CASCADE)
    tags = TagsField(max_length=100, blank=True)

    def tag_list(self, delimiter=','):
        return self.tags.split(delimiter) if len(self.tags) > 0 else []

    class Meta:
        verbose_name_plural = 'notes'

    def __str__(self):
        return self.title + ' (id=' + str(self.id) + ')'


class UserProfile(Model):
    syntax_highlighting_style = CharField(max_length=8, choices=SYNTAX_HIGHLIGHTING_CHOICES,
                                          default=SYNTAX_HIGHLIGHTING_CHOICES[0][1])
    theme = CharField(max_length=5, choices=THEME_CHOICES, default=THEME_CHOICES[0][1])
    user = ForeignKey(User, on_delete=CASCADE)

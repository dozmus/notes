from colorful.fields import RGBColorField
from django.contrib.auth.models import User
from django.db.models import Model, CharField, TextField, ForeignKey, CASCADE, BooleanField
from django_tagify.fields import TagsField

from notes.compact_mode import ON_OFF_CHOICES
from notes.syntax_highlighting import SYNTAX_HIGHLIGHTING_CHOICES
from notes.themes import THEME_CHOICES


class Notebook(Model):
    title = CharField(max_length=200)
    colour = RGBColorField()
    owner = ForeignKey(User, related_name='notebooks', on_delete=CASCADE)

    class Meta:
        verbose_name_plural = 'notebooks'

    def __str__(self):
        return self.title + ' (id=' + str(self.id) + ')'


class Note(Model):
    title = CharField(max_length=250)
    content = TextField(max_length=10000)
    notebook = ForeignKey(Notebook, related_name='notes', on_delete=CASCADE)
    trash = BooleanField(default=False)
    tags = TagsField(max_length=200, blank=True)

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
    compact_mode = CharField(max_length=3, choices=ON_OFF_CHOICES, default='Off')
    user = ForeignKey(User, on_delete=CASCADE)

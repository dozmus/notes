from colorful.fields import RGBColorField
from django.contrib.auth.models import User
from django.db.models import Model, CharField, TextField, ForeignKey, CASCADE

from notes.syntax_highlighting import SYNTAX_HIGHLIGHTING_CHOICES


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
    content = TextField(max_length=10000)
    notebook = ForeignKey(Notebook, on_delete=CASCADE)

    class Meta:
        verbose_name_plural = 'notes'

    def __str__(self):
        return self.title + ' (id=' + str(self.id) + ')'


class UserProfile(Model):
    syntax_highlighting_style = CharField(max_length=8, choices=SYNTAX_HIGHLIGHTING_CHOICES,
                                          default=SYNTAX_HIGHLIGHTING_CHOICES[0][1])
    user = ForeignKey(User, on_delete=CASCADE)

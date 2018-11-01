from colorful.fields import RGBColorField
from django.contrib.auth.models import User
from django.db.models import Model, CharField, TextField, ForeignKey, CASCADE, BooleanField, Manager, QuerySet
from django_tagify.fields import TagsField

from notes.compact_mode import ON_OFF_CHOICES
from notes.syntax_highlighting import SYNTAX_HIGHLIGHTING_CHOICES
from notes.themes import THEME_CHOICES


class NotebookManager(Manager):
    def for_user(self, user):
        if user.is_authenticated:
            return Notebook.objects.filter(owner=user).order_by('id')
        return QuerySet()


class NoteManager(Manager):
    def for_user(self, user):
        if user.is_authenticated:
            return Note.objects.filter(notebook__owner=user).order_by('id')
        return QuerySet()

    def search(self, user, query, notebook=None):
        if not user.is_authenticated:
            return []

        # Get notes to search
        notes = self.for_user(user)

        if notebook is not None:
            notes = notes.filter(notebook_id=notebook.id)

        # Compute results
        results = []

        for note in notes:
            if query in note.title or query in note.content or query in note.tag_list():
                results.append(note)
        return results


class TrashNoteManager(Manager):
    def get_queryset(self):
        return super(TrashNoteManager, self).get_queryset().filter(trash=True).order_by('id')

    def for_user(self, user):
        if user.is_authenticated:
            return TrashNote.objects.filter(notebook__owner=user)
        return QuerySet()

    def search(self, user, query):
        if not user.is_authenticated:
            return []

        owners_notes = TrashNote.objects.filter(notebook__owner=user)

        # Compute results
        results = []

        for note in owners_notes:
            if query in note.title or query in note.content or query in note.tag_list():
                results.append(note)
        return results


class Notebook(Model):
    objects = NotebookManager()

    title = CharField(max_length=200)
    colour = RGBColorField()
    owner = ForeignKey(User, related_name='notebooks', on_delete=CASCADE)

    class Meta:
        verbose_name_plural = 'notebooks'

    def __str__(self):
        return self.title + ' (id=' + str(self.id) + ')'


class Note(Model):
    objects = NoteManager()

    title = CharField(max_length=250)
    content = TextField(max_length=10000)
    notebook = ForeignKey(Notebook, related_name='notes', on_delete=CASCADE)
    trash = BooleanField(default=False)
    tags = TagsField(max_length=200, blank=True)

    @classmethod
    def delete_all(cls, notes):
        for note in notes:
            note.delete()

    @classmethod
    def trash_all(cls, notes):
        for note in notes:
            note.trash = True
            note.save()

    @classmethod
    def untrash_all(cls, notes):
        for note in notes:
            note.trash = False
            note.save()

    def tag_list(self, delimiter=','):
        return self.tags.split(delimiter) if len(self.tags) > 0 else []

    class Meta:
        verbose_name_plural = 'notes'

    def __str__(self):
        return self.title + ' (id=' + str(self.id) + ')'


class TrashNote(Note):
    objects = TrashNoteManager()

    class Meta:
        proxy = True


class UserProfile(Model):
    syntax_highlighting_style = CharField(max_length=8, choices=SYNTAX_HIGHLIGHTING_CHOICES,
                                          default=SYNTAX_HIGHLIGHTING_CHOICES[0][1])
    theme = CharField(max_length=5, choices=THEME_CHOICES, default=THEME_CHOICES[0][1])
    compact_mode = CharField(max_length=3, choices=ON_OFF_CHOICES, default='Off')
    user = ForeignKey(User, on_delete=CASCADE)

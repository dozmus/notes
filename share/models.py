from django.db.models import Model, CharField, DateTimeField, ForeignKey, CASCADE

from notes.models import Note


class SharableLink(Model):
    PERMISSIONS_CHOICES = (('read', 'read'), ('read+write', 'read+write'))
    code = CharField(max_length=32, unique=True)
    permissions = CharField(max_length=10, choices=PERMISSIONS_CHOICES)
    expiry_date = DateTimeField()
    note = ForeignKey(Note, on_delete=CASCADE)

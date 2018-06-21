from django.db.models import QuerySet

from notes.models import Notebook, Note


def notebooks(request):
    user = request.user

    if user.is_authenticated:
        return Notebook.objects.filter(owner=user).order_by('id')
    else:
        return QuerySet()


def notes(request):
    user = request.user

    if user.is_authenticated:
        return Note.objects.filter(notebook__owner=user).order_by('id')
    else:
        return QuerySet()

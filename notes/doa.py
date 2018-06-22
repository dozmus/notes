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


def search_notes(request, query, notebook=None):
    user = request.user

    if user.is_authenticated:
        owners_notes = Note.objects.filter(notebook__owner=user)

        if notebook is not None:
            owners_notes = owners_notes.filter(notebook_id=notebook.id)

        by_title = owners_notes.filter(title__contains=query).order_by('id')
        by_content = owners_notes.filter(content__contains=query).order_by('id')
        return by_title | by_content
    else:
        return QuerySet()

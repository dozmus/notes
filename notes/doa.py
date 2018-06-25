from typing import List

from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import Http404

from notes.models import Notebook, Note


def notebooks(user: User) -> QuerySet:
    """
    Returns all notebooks belonging to the argument user if they are authenticated, otherwise it returns an empty
    QuerySet.
    """
    if user.is_authenticated:
        return Notebook.objects.filter(owner=user).order_by('id')
    else:
        return QuerySet()


def notes(user: User) -> QuerySet:
    """
    Returns all note belonging to the argument user if they are authenticated, otherwise it returns an empty QuerySet.
    """
    if user.is_authenticated:
        return Note.objects.filter(notebook__owner=user).order_by('id')
    else:
        return QuerySet()


def search_notes(user: User, query: str, notebook: Notebook=None) -> QuerySet:
    """
    Returns all note belonging to the argument user if they are authenticated, otherwise it returns an empty QuerySet.
    The notes it returns are those whose title or content contains the search query.
    If the argument notebook is specified, only notes in it are searched.
    """
    if user.is_authenticated:
        owners_notes = Note.objects.filter(notebook__owner=user)

        if notebook is not None:
            owners_notes = owners_notes.filter(notebook_id=notebook.id)

        by_title = owners_notes.filter(title__contains=query).order_by('id')
        by_content = owners_notes.filter(content__contains=query).order_by('id')
        return by_title | by_content
    else:
        return QuerySet()


def validate_ownership_notebook(user: User, notebook_id: int) -> Notebook:
    """
    Returns the notebook with the argument id if the argument user owns it.
    :raises Http404: If the notebook does not exist, or the user does not have access to it.
    """
    # Check notebook exists
    try:
        notebook = Notebook.objects.filter(id=notebook_id).get()
    except:
        raise Http404('Notebook does not exist.')

    # Check owner of notebook
    if user.username != notebook.owner.username:
        raise Http404('Notebook does not exist.')
    return notebook


def validate_ownership_note(user: User, note_id: int) -> Note:
    """
    Returns the note with the argument id if the argument user owns it.
    :raises Http404: If the note does not exist, or the user does not have access to it.
    """
    # Check note exists
    try:
        note = Note.objects.filter(id=note_id).get()
    except:
        raise Http404('Note does not exist.')

    # Check owner of note
    if user.username != note.notebook.owner.username:
        raise Http404('Note does not exist.')
    return note


def validate_ownership_notes(user: User, note_ids: List[int]) -> List[Note]:
    """
    Returns a list of the notes which correspond to the argument note ids, if the argument user owns all of them.
    :raises Http404: If any note does not exist, or the user does not have access to any of them.
    """
    # Collect valid nodes
    valid_notes = []

    for note_id in note_ids:
        current_note = validate_ownership_note(user, note_id)
        valid_notes.append(current_note)
    return valid_notes

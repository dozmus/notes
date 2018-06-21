from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect

from .models import Note, Notebook
from .forms import NoteForm, NotebookForm
from .doa import notebooks, notes


def home(request):
    context = {
        'notebooks': notebooks(request),
        'notes': notes(request)
    }
    return render(request, 'home.html', context)


@login_required
def new_notebook(request):
    if request.method != 'POST':
        form = NotebookForm()
    else:
        form = NotebookForm(data=request.POST)

        if form.is_valid():
            notebook = form.save(commit=False)
            notebook.owner = request.user
            notebook.save()
            return redirect('home')

    context = {
        'form': form,
        'notebooks': notebooks(request),
        'notes': notes(request)
    }
    return render(request, 'new_notebook.html', context)


@login_required
def new_note(request):
    if request.method != 'POST':
        form = NoteForm()
    else:
        form = NoteForm(data=request.POST)

        if form.is_valid():
            form.save()
            return redirect('home')

    context = {
        'form': form,
        'notebooks': notebooks(request),
        'notes': notes(request)
    }
    return render(request, 'new_note.html', context)


@login_required
def view_note(request, note_id):
    # Check note exists
    try:
        current_note = Note.objects.filter(id=note_id).get()
    except:
        raise Http404('Note does not exist.')

    # Check owner of note
    note_owner = current_note.notebook.owner

    if request.user.username != note_owner.username:
        raise Http404('Note does not exist.')

    # Render
    context = {
        'notebooks': notebooks(request),
        'notes': notes(request),
        'current_note': current_note,
    }
    return render(request, 'view_note.html', context)


@login_required
def view_notebook(request, notebook_id):
    # Check notebook exists
    try:
        current_notebook = Notebook.objects.filter(id=notebook_id).get()
    except:
        raise Http404('Notebook does not exist.')

    # Check owner of notebook
    note_owner = current_notebook.owner

    if request.user.username != note_owner.username:
        raise Http404('Notebook does not exist.')

    # Render
    context = {
        'notebooks': notebooks(request),
        'notes': Note.objects.filter(notebook_id=notebook_id).order_by('id'),
        'current_notebook': current_notebook
    }
    return render(request, 'view_notebook.html', context)


@login_required
def edit_note(request, note_id):
    # Check note exists
    try:
        current_note = Note.objects.filter(id=note_id).get()
    except:
        raise Http404('Note does not exist.')

    # Check owner of note
    note_owner = current_note.notebook.owner

    if request.user.username != note_owner.username:
        raise Http404('Note does not exist.')

    # Create form
    if request.method != 'POST':
        form = NoteForm(data={
            'title': current_note.title,
            'notebook': current_note.notebook,
            'content': current_note.content
        })
    else:
        form = NoteForm(data=request.POST)

        if form.is_valid():
            current_note.title = form.cleaned_data['title']
            current_note.notebook = form.cleaned_data['notebook']
            current_note.content = form.cleaned_data['content']
            current_note.save()
            return redirect('home')

    context = {
        'form': form,
        'notebooks': notebooks(request),
        'notes': notes(request),
        'current_note': current_note
    }
    return render(request, 'edit_note.html', context)


@login_required
def delete_note(request, note_id):
    # Check note exists
    try:
        current_note = Note.objects.filter(id=note_id).get()
    except:
        raise Http404('Note does not exist.')

    # Check owner of note
    note_owner = current_note.notebook.owner

    if request.user.username != note_owner.username:
        raise Http404('Note does not exist.')

    if request.method == 'POST':
        current_note.delete()
        return redirect('home')

    # Render
    context = {
        'notebooks': notebooks(request),
        'notes': notes(request),
        'current_note': current_note
    }
    return render(request, 'delete_note.html', context)


@login_required
def edit_notebook(request, notebook_id):
    # Check notebook exists
    try:
        current_notebook = Notebook.objects.filter(id=notebook_id).get()
    except:
        raise Http404('Notebook does not exist.')

    # Check owner of notebook
    note_owner = current_notebook.owner

    if request.user.username != note_owner.username:
        raise Http404('Notebook does not exist.')

    # Create form
    if request.method != 'POST':
        form = NotebookForm(data={
            'title': current_notebook.title
        })
    else:
        form = NotebookForm(data=request.POST)

        if form.is_valid():
            current_notebook.title = form.cleaned_data['title']
            current_notebook.save()
            return redirect('home')

    context = {
        'form': form,
        'notebooks': notebooks(request),
        'notes': notes(request),
        'current_notebook': current_notebook
    }
    return render(request, 'edit_notebook.html', context)


@login_required
def delete_notebook(request, notebook_id):
    # Check notebook exists
    try:
        current_notebook = Notebook.objects.filter(id=notebook_id).get()
    except:
        raise Http404('Notebook does not exist.')

    # Check owner of notebook
    note_owner = current_notebook.owner

    if request.user.username != note_owner.username:
        raise Http404('Notebook does not exist.')

    if request.method == 'POST':
        current_notebook.delete()
        return redirect('home')

    # Render
    context = {
        'notebooks': notebooks(request),
        'notes': notes(request),
        'current_notebook': current_notebook
    }
    return render(request, 'delete_notebook.html', context)

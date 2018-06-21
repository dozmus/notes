from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import Note, Notebook
from .forms import NoteForm, NotebookForm


def home(request):
    context = {
        'notebooks': Notebook.objects.all().order_by('id'),
        'notes': Note.objects.all().order_by('id')
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
        'notebooks': Notebook.objects.all().order_by('id'),
        'notes': Note.objects.all().order_by('id')
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
        'notebooks': Notebook.objects.all().order_by('id'),
        'notes': Note.objects.all().order_by('id')
    }
    return render(request, 'new_note.html', context)


@login_required
def view_note(request, note_id):
    context = {
        'notebooks': Notebook.objects.all().order_by('id'),
        'notes': Note.objects.all().order_by('id'),
        'current_note': Note.objects.filter(id=note_id).get(),
    }
    # TODO note exists AND owner of note => else: raise 'clean' 404 error
    return render(request, 'view_note.html', context)


@login_required
def view_notebook(request, notebook_id):
    context = {
        'notebooks': Notebook.objects.all().order_by('id'),
        'notes': Note.objects.filter(notebook_id=notebook_id).order_by('id'),
        'current_notebook': Notebook.objects.filter(id=notebook_id).get()
    }
    # TODO notebook exists AND owner of notebook => else: raise 'clean' 404 error
    return render(request, 'view_notebook.html', context)

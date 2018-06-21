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

    context = {'form': form}
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

    context = {'form': form}
    return render(request, 'new_note.html', context)


# def delete_note(request, note_id):
#     return HttpResponse('delete_note ' + str(note_id))
#
#
# def delete_notebook(request, notebook_id):
#     return HttpResponse('delete_notebook ' + str(notebook_id))
#
#
# def login(request):
#     return HttpResponse('login')
#
#
# def perform_login(request):
#     return HttpResponse('perform_login')
#
#
# def logout(request):
#     return HttpResponse('logout')
#
#
# def register(request):
#     return HttpResponse('register')

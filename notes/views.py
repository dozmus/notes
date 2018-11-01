from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from notes.doa import validate_ownership_notebook, validate_ownership_note, validate_ownership_notes
from notes.file_response_provider import note2txt_response, note2pdf_response, render_markdown, notebook2txtzip_response, \
    notebook2pdfzip_response, notes2pdfzip_response, notes2txtzip_response
from .models import Note, UserProfile
from .forms import NoteForm, NotebookForm, SelectNotesForm, SelectNotebookForm, UserProfileForm
from .user_profiles import regular_context


def home(request):
    context = regular_context(request.user)
    return render(request, 'home.html', context)


@login_required
def edit_profile(request):
    profile = UserProfile.objects.filter(user=request.user).get()

    # Create form
    if request.method != 'POST':
        form = UserProfileForm(data={
            'theme': profile.theme,
            'syntax_highlighting_style': profile.syntax_highlighting_style,
            'compact_mode': profile.compact_mode,
        })
    else:
        form = UserProfileForm(data=request.POST)

        if form.update(profile):
            return redirect('home')

    # Render
    context = regular_context(request.user)
    context['form'] = form
    return render(request, 'edit_profile.html', context)


@login_required
def new_notebook(request):
    if request.method != 'POST':
        form = NotebookForm()
    else:
        form = NotebookForm(data=request.POST)

        if form.create(request.user):
            return redirect('home')

    # Render
    context = regular_context(request.user)
    context['form'] = form
    return render(request, 'new_notebook.html', context)


@login_required
def new_note(request):
    if request.method != 'POST':
        form = NoteForm()
        form.restrict_to_user(request.user)
    else:
        form = NoteForm(data=request.POST)
        form.restrict_to_user(request.user)

        if form.create():
            return redirect('home')

    # Render
    context = regular_context(request.user)
    context['form'] = form
    return render(request, 'new_note.html', context)


@login_required
def view_note(request, note_id):
    # Validate note
    current_note = validate_ownership_note(request.user, note_id)

    # Render
    current_note.rendered_content = render_markdown(current_note.content)

    context = regular_context(request.user)
    context['current_note'] = current_note
    return render(request, 'view_note.html', context)


@login_required
def download_note(request, note_id, filetype):
    # Validate note
    current_note = validate_ownership_note(request.user, note_id)

    # Return file
    if filetype == 'txt':
        return note2txt_response(current_note)
    elif filetype == 'pdf':
        return note2pdf_response(request, current_note)
    else:
        raise Http404('Invalid filetype.')


@login_required
def move_notes(request, note_ids):
    # Validate notes
    note_id_array = note_ids.split(',')
    notes = validate_ownership_notes(request.user, note_id_array)

    # Create form
    if request.method != 'POST':
        form = SelectNotebookForm()
        form.restrict_to_user(request.user)
    else:
        form = SelectNotebookForm(data=request.POST)

        if form.move(notes):
            return redirect('home')

    # Render
    context = regular_context(request.user)
    context['notes'] = notes
    context['form'] = form
    context['current_note_ids'] = note_ids
    return render(request, 'move_notes.html', context)


@login_required
def delete_notes(request, note_ids):
    # Validate notes
    note_id_array = note_ids.split(',')
    notes = validate_ownership_notes(request.user, note_id_array)

    if request.method == 'POST':
        Note.trash_all(notes)
        return redirect('home')

    # Render
    context = regular_context(request.user)
    context['notes'] = notes
    context['current_note_ids'] = note_ids
    return render(request, 'delete_notes.html', context)


@login_required
def view_notebook(request, notebook_id):
    # Validate notebook
    current_notebook = validate_ownership_notebook(request.user, notebook_id)

    # Create form
    notes = Note.objects.filter(notebook_id=notebook_id, trash=False).order_by('id')

    if request.method != 'POST':
        form = SelectNotesForm()
        form.set_choices(notes)
    else:
        form = SelectNotesForm(data=request.POST)
        form.set_choices(notes)

        if form.is_valid():
            # Collect valid nodes
            valid_notes = validate_ownership_notes(request.user, form.cleaned_data['picked'])
            note_ids = ','.join([str(note.id) for note in valid_notes])

            if len(valid_notes) > 0:
                # Download
                if 'downloadtxts' in request.POST:
                    return notes2txtzip_response(valid_notes, 'notes-%s-partial' % current_notebook.title)

                # Download
                if 'downloadpdfs' in request.POST:
                    return notes2pdfzip_response(valid_notes, 'notes-%s-partial' % current_notebook.title)

                # Move
                if 'merge' in request.POST:
                    return HttpResponseRedirect(reverse('merge-notes', kwargs={'note_ids': note_ids}))

                # Move
                if 'move' in request.POST:
                    return HttpResponseRedirect(reverse('move-notes', kwargs={'note_ids': note_ids}))

                # Delete
                if 'delete' in request.POST:
                    return HttpResponseRedirect(reverse('delete-notes', kwargs={'note_ids': note_ids}))

    # Render
    context = regular_context(request.user)
    context['form'] = form
    context['notes'] = notes
    context['current_notebook'] = current_notebook
    return render(request, 'view_notebook.html', context)


@login_required
def merge_notes(request, note_ids):
    # Validate notes
    note_id_array = note_ids.split(',')
    notes = validate_ownership_notes(request.user, note_id_array)

    # Merge data
    merged_contents = ''
    merged_tags = ''

    for note in notes:
        merged_contents += note.content + '\r\n'
        merged_tags += ',' + note.tags if merged_tags else note.tags

    # Create form
    if request.method != 'POST':
        form = NoteForm(data={
            'title': notes[0].title,
            'content': merged_contents,
            'notebook': notes[0].notebook,
            'tags': merged_tags,
        })
        form.restrict_to_user(request.user)
    else:
        form = NoteForm(data=request.POST)

        if form.create():
            Note.delete_all(notes)
            return redirect('home')

    # Render
    context = regular_context(request.user)
    context['notes'] = notes
    context['form'] = form
    context['current_note_ids'] = note_ids
    return render(request, 'merge_notes.html', context)


@login_required
def edit_note(request, note_id):
    # Validate note
    current_note = validate_ownership_note(request.user, note_id)

    # Create form
    if request.method != 'POST':
        form = NoteForm(data={
            'title': current_note.title,
            'notebook': current_note.notebook,
            'content': current_note.content,
            'tags': current_note.tags,
        })
        form.restrict_to_user(request.user)
    else:
        form = NoteForm(data=request.POST)
        form.restrict_to_user(request.user)

        if form.update(current_note):
            return HttpResponseRedirect(reverse('view-note', kwargs={'note_id': note_id}))

    # Render
    context = regular_context(request.user)
    context['form'] = form
    context['current_note'] = current_note
    return render(request, 'edit_note.html', context)


@login_required
def delete_note(request, note_id):
    # Validate note
    current_note = validate_ownership_note(request.user, note_id)

    if request.method == 'POST':
        current_note.trash = True
        current_note.save()
        return redirect('home')

    # Render
    context = regular_context(request.user)
    context['current_note'] = current_note
    return render(request, 'delete_note.html', context)


@login_required
def edit_notebook(request, notebook_id):
    # Validate notebook
    current_notebook = validate_ownership_notebook(request.user, notebook_id)

    # Create form
    if request.method != 'POST':
        form = NotebookForm(data={
            'title': current_notebook.title,
            'colour': current_notebook.colour
        })
    else:
        form = NotebookForm(data=request.POST)

        if form.update(current_notebook):
            return redirect('home')

    # Render
    context = regular_context(request.user)
    context['form'] = form
    context['current_notebook'] = current_notebook
    return render(request, 'edit_notebook.html', context)


@login_required
def delete_notebook(request, notebook_id):
    # Validate notebook
    current_notebook = validate_ownership_notebook(request.user, notebook_id)

    if request.method == 'POST':
        current_notebook.delete()
        return redirect('home')

    # Render
    context = regular_context(request.user)
    context['current_notebook'] = current_notebook
    return render(request, 'delete_notebook.html', context)


@login_required
def download_notebook(request, notebook_id, filetype):
    # Validate notebook
    current_notebook = validate_ownership_notebook(request.user, notebook_id)

    # Return file
    if filetype == 'txt':
        return notebook2txtzip_response(current_notebook)
    elif filetype == 'pdf':
        return notebook2pdfzip_response(current_notebook)
    else:
        raise Http404('Invalid filetype.')


@login_required
def search(request):
    if request.method != 'POST':
        return redirect('home')

    # Render
    query = request.POST['query']

    context = regular_context(request.user)
    context['query'] = query
    context['notes'] = Note.objects.search(request.user, query)
    return render(request, 'search.html', context)


@login_required
def search_notebook(request, notebook_id):
    if request.method != 'POST':
        return redirect('home')

    # Validate notebook
    current_notebook = validate_ownership_notebook(request.user, notebook_id)

    # Render
    query = request.POST['query']

    context = regular_context(request.user)
    context['query'] = query
    context['notes'] = Note.objects.search(request.user, query, current_notebook)
    context['current_notebook'] = current_notebook
    return render(request, 'search_notebook.html', context)

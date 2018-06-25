import random
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.timezone import utc

from notes.file_response_provider import note2txt_response, note2pdf_response, render_markdown, notebook2txtzip, \
    notebook2pdfzip, notes2pdfzip_response, notes2txtzip_response
from notes.syntax_highlighting import stylesheet_link
from .models import Note, Notebook, UserProfile, SharableLink
from .forms import NoteForm, NotebookForm, SelectNotesForm, SelectNotebookForm, UserProfileForm, SharableLinkForm, \
    SharedNoteForm, EditSharableLinkForm
from .doa import notebooks, notes, search_notes


def home(request):
    context = {
        'notebooks': notebooks(request),
        'notes': notes(request)
    }
    return render(request, 'home.html', context)


@login_required
def edit_profile(request):
    profile = UserProfile.objects.filter(user=request.user).get()

    # Create form
    if request.method != 'POST':
        form = UserProfileForm(data={
            'syntax_highlighting_style': profile.syntax_highlighting_style
        })
    else:
        form = UserProfileForm(data=request.POST)

        if form.is_valid():
            profile.syntax_highlighting_style = form.cleaned_data['syntax_highlighting_style']
            profile.save()
            return redirect('home')

    # Render
    context = {
        'form': form,
        'notebooks': notebooks(request),
        'notes': notes(request),
    }
    return render(request, 'edit_profile.html', context)


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

    # Render
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
        form.restrict_to_user(request.user)
    else:
        form = NoteForm(data=request.POST)

        if form.is_valid():
            form.save()
            return redirect('home')

    # Render
    context = {
        'form': form,
        'notebooks': notebooks(request),
        'notes': notes(request)
    }
    return render(request, 'new_note.html', context)


@login_required
def view_note(request, note_id):
    # Validate note
    current_note = validate_ownership_note(request, note_id)

    # Render
    profile = UserProfile.objects.filter(user=request.user).get()
    current_note.rendered_content = render_markdown(current_note.content)
    context = {
        'notebooks': notebooks(request),
        'notes': notes(request),
        'current_note': current_note,
        'syntax_highlighting_stylesheet': stylesheet_link(profile.syntax_highlighting_style)
    }
    return render(request, 'view_note.html', context)


@login_required
def share_note(request, note_id):
    # Validate note
    current_note = validate_ownership_note(request, note_id)

    # Render
    sharable_links = current_note.sharablelink_set.all()

    for link in sharable_links:
        args = {'note_id': current_note.id, 'code': link.code}
        link.full_url = request.build_absolute_uri(reverse('view-shared-note', kwargs=args))

    profile = UserProfile.objects.filter(user=request.user).get()
    current_note.rendered_content = render_markdown(current_note.content)
    context = {
        'notebooks': notebooks(request),
        'notes': notes(request),
        'current_note': current_note,
        'syntax_highlighting_stylesheet': stylesheet_link(profile.syntax_highlighting_style),
        'sharable_links': sharable_links,
    }
    return render(request, 'share_note.html', context)


@login_required
def new_share_link(request, note_id):
    # Validate note
    current_note = validate_ownership_note(request, note_id)

    if request.method != 'POST':
        form = SharableLinkForm()

        # Generate unique code
        unique_code = '%32x' % random.getrandbits(16 * 8)
        entry = SharableLink.objects.filter(code=unique_code)

        while entry.exists():
            unique_code = '%32x' % random.getrandbits(16 * 8)
            entry = SharableLink.objects.filter(code=unique_code)

        form.set_code(unique_code)
    else:
        form = SharableLinkForm(data=request.POST)

        if form.is_valid():
            SharableLink.objects.create(note_id=note_id, code=form.cleaned_data['code'],
                                        permissions=form.cleaned_data['permissions'],
                                        expiry_date=form.cleaned_data['expiry_date'])
            return redirect('home')

    # Render
    context = {
        'form': form,
        'notebooks': notebooks(request),
        'notes': notes(request),
        'current_note': current_note
    }
    return render(request, 'new_share_link.html', context)


@login_required
def edit_share_link(request, note_id, code):
    # Validate note
    current_note = validate_ownership_note(request, note_id)
    link = SharableLink.objects.filter(code=code).filter(note_id=note_id).get()

    if request.method != 'POST':
        form = EditSharableLinkForm(data={
            'permissions': link.permissions,
            'expiry_date': link.expiry_date
        })
    else:
        form = EditSharableLinkForm(data=request.POST)

        if form.is_valid():
            link.permissions = form.cleaned_data['permissions']
            link.expiry_date = form.cleaned_data['expiry_date']
            link.save()
            return redirect('home')

    # Render
    context = {
        'form': form,
        'notebooks': notebooks(request),
        'notes': notes(request),
        'current_note': current_note,
        'code': code
    }
    return render(request, 'edit_share_link.html', context)


def edit_shared_note(request, note_id, code):
    # Validate note
    note, sharable_link = validate_ownership_shared_note(request, note_id, code)

    # Create form
    if request.method != 'POST':
        form = SharedNoteForm(data={
            'title': note.title,
            'content': note.content
        })
    else:
        form = SharedNoteForm(data=request.POST)

        if form.is_valid() and sharable_link.permissions == 'read+write':
            note.title = form.cleaned_data['title']
            note.content = form.cleaned_data['content']
            note.save()
            return redirect('home')

    # Render
    context = {
        'form': form,
        'notebooks': notebooks(request),
        'notes': notes(request),
        'current_note': note,
        'code': code
    }
    return render(request, 'edit_shared_note.html', context)


def delete_shared_note(request, note_id, code):
    # Validate note
    note, sharable_link = validate_ownership_shared_note(request, note_id, code)

    if request.method == 'POST' and sharable_link.permissions == 'read+write':
        note.delete()
        return redirect('home')

    # Render
    context = {
        'notebooks': notebooks(request),
        'notes': notes(request),
        'current_note': note,
        'code': code,
    }
    return render(request, 'delete_shared_note.html', context)


@login_required
def delete_share_link(request, note_id, code):
    # Validate note
    note, sharable_link = validate_ownership_shared_note(request, note_id, code)

    if request.method == 'POST':
        sharable_link.delete()
        return redirect('home')

    # Render
    context = {
        'notebooks': notebooks(request),
        'notes': notes(request),
        'current_note': note,
        'code': code,
    }
    return render(request, 'delete_share_link.html', context)


def download_shared_note(request, note_id, filetype, code):
    # Validate note
    note, sharable_link = validate_ownership_shared_note(request, note_id, code)

    # Return file
    if filetype == 'txt':
        return note2txt_response(note)
    elif filetype == 'pdf':
        return note2pdf_response(request, note)
    else:
        raise Http404('Invalid filetype.')


def view_shared_note(request, note_id, code):
    # Validate note
    note, sharable_link = validate_ownership_shared_note(request, note_id, code)

    # Stylesheet
    if request.user.is_authenticated:
        syntax_highlighting_style = UserProfile.objects.filter(user=request.user).get().syntax_highlighting_style
    else:
        syntax_highlighting_style = stylesheet_link([])

    # Render
    note.rendered_content = render_markdown(note.content)
    context = {
        'notebooks': notebooks(request),
        'notes': notes(request),
        'current_note': note,
        'syntax_highlighting_stylesheet': syntax_highlighting_style,
        'code': sharable_link.code,
        'permissions': sharable_link.permissions,
    }
    return render(request, 'view_shared_note.html', context)


@login_required
def download_note(request, note_id, filetype):
    # Validate note
    current_note = validate_ownership_note(request, note_id)

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
    notes = validate_ownership_notes(request, note_id_array)

    # Create form
    if request.method != 'POST':
        form = SelectNotebookForm()
        form.restrict_to_user(request.user)
    else:
        form = SelectNotebookForm(data=request.POST)

        if form.is_valid():
            for note in notes:
                note.notebook = form.cleaned_data['notebook']
                note.save()
            return redirect('home')

    # Render
    context = {
        'form': form,
        'notebooks': notebooks(request),
        'notes': notes,
        'current_note_ids': note_ids
    }
    return render(request, 'move_notes.html', context)


@login_required
def delete_notes(request, note_ids):
    # Validate notes
    note_id_array = note_ids.split(',')
    notes = validate_ownership_notes(request, note_id_array)

    if request.method == 'POST':
        for note in notes:
            note.delete()
        return redirect('home')

    # Render
    context = {
        'notebooks': notebooks(request),
        'notes': notes,
        'current_note_ids': note_ids
    }
    return render(request, 'delete_notes.html', context)


@login_required
def view_notebook(request, notebook_id):
    # Validate notebook
    current_notebook = validate_ownership_notebook(request, notebook_id)

    # Create form
    notes = Note.objects.filter(notebook_id=notebook_id).order_by('id')

    if request.method != 'POST':
        form = SelectNotesForm()
        form.set_choices(notes)
    else:
        form = SelectNotesForm(data=request.POST)
        form.set_choices(notes)

        if form.is_valid():
            # Collect valid nodes
            valid_notes = validate_ownership_notes(request, form.cleaned_data['picked'])

            if len(valid_notes) > 0:
                # Download
                if 'downloadtxts' in request.POST:
                    return notes2txtzip_response(valid_notes, 'notes-%s-partial' % current_notebook.title)

                # Download
                if 'downloadpdfs' in request.POST:
                    return notes2pdfzip_response(valid_notes, 'notes-%s-partial' % current_notebook.title)

                # Move
                if 'move' in request.POST:
                    note_ids = ','.join([str(note.id) for note in valid_notes])
                    return HttpResponseRedirect(reverse('move-notes', kwargs={'note_ids': note_ids}))

                # Delete
                if 'delete' in request.POST:
                    note_ids = ','.join([str(note.id) for note in valid_notes])
                    return HttpResponseRedirect(reverse('delete-notes', kwargs={'note_ids': note_ids}))

    # Render
    context = {
        'form': form,
        'notebooks': notebooks(request),
        'notes': notes,
        'current_notebook': current_notebook
    }
    return render(request, 'view_notebook.html', context)


@login_required
def edit_note(request, note_id):
    # Validate note
    current_note = validate_ownership_note(request, note_id)

    # Create form
    if request.method != 'POST':
        form = NoteForm(data={
            'title': current_note.title,
            'notebook': current_note.notebook,
            'content': current_note.content
        })
        form.restrict_to_user(request.user)
    else:
        form = NoteForm(data=request.POST)

        if form.is_valid():
            current_note.title = form.cleaned_data['title']
            current_note.notebook = form.cleaned_data['notebook']
            current_note.content = form.cleaned_data['content']
            current_note.save()
            return redirect('home')

    # Render
    context = {
        'form': form,
        'notebooks': notebooks(request),
        'notes': notes(request),
        'current_note': current_note
    }
    return render(request, 'edit_note.html', context)


@login_required
def delete_note(request, note_id):
    # Validate note
    current_note = validate_ownership_note(request, note_id)

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
    # Validate notebook
    current_notebook = validate_ownership_notebook(request, notebook_id)

    # Create form
    if request.method != 'POST':
        form = NotebookForm(data={
            'title': current_notebook.title,
            'colour': current_notebook.colour
        })
    else:
        form = NotebookForm(data=request.POST)

        if form.is_valid():
            current_notebook.title = form.cleaned_data['title']
            current_notebook.colour = form.cleaned_data['colour']
            current_notebook.save()
            return redirect('home')

    # Render
    context = {
        'form': form,
        'notebooks': notebooks(request),
        'notes': notes(request),
        'current_notebook': current_notebook
    }
    return render(request, 'edit_notebook.html', context)


@login_required
def delete_notebook(request, notebook_id):
    # Validate notebook
    current_notebook = validate_ownership_notebook(request, notebook_id)

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


@login_required
def download_notebook(request, notebook_id, filetype):
    # Validate notebook
    current_notebook = validate_ownership_notebook(request, notebook_id)

    # Return file
    if filetype == 'txt':
        return notebook2txtzip(current_notebook)
    elif filetype == 'pdf':
        return notebook2pdfzip(current_notebook)
    else:
        raise Http404('Invalid filetype.')


@login_required
def search(request):
    if request.method != 'POST':
        return redirect('home')

    # Render
    query = request.POST['query']

    context = {
        'notebooks': notebooks(request),
        'notes': search_notes(request, query),
        'query': query
    }
    return render(request, 'search.html', context)


@login_required
def search_notebook(request, notebook_id):
    if request.method != 'POST':
        return redirect('home')

    # Validate notebook
    current_notebook = validate_ownership_notebook(request, notebook_id)

    # Render
    query = request.POST['query']

    context = {
        'notebooks': notebooks(request),
        'notes': search_notes(request, query, current_notebook),
        'current_notebook': current_notebook,
        'query': query
    }
    return render(request, 'search_notebook.html', context)


def validate_ownership_notebook(request, notebook_id):
    # Check notebook exists
    try:
        notebook = Notebook.objects.filter(id=notebook_id).get()
    except:
        raise Http404('Notebook does not exist.')

    # Check owner of notebook
    note_owner = notebook.owner

    if request.user.username != note_owner.username:
        raise Http404('Notebook does not exist.')
    return notebook


def validate_ownership_note(request, note_id):
    # Check note exists
    try:
        note = Note.objects.filter(id=note_id).get()
    except:
        raise Http404('Note does not exist.')

    # Check owner of note
    note_owner = note.notebook.owner

    if request.user.username != note_owner.username:
        raise Http404('Note does not exist.')
    return note


def validate_ownership_shared_note(request, note_id, code):
    # Get sharable link and note
    try:
        note = Note.objects.filter(id=note_id).get()
        sharable_link = SharableLink.objects.filter(note_id=note_id).filter(code=code).get()
    except:
        raise Http404('Note does not exist.')

    # Check expiry date
    if sharable_link.expiry_date < utc.localize(datetime.now()):
        raise Http404('This share link has expired.')
    return note, sharable_link


def validate_ownership_notes(request, note_ids):
    # Collect valid nodes
    valid_notes = []

    for note_id in note_ids:
        current_note = validate_ownership_note(request, note_id)
        valid_notes.append(current_note)
    return valid_notes

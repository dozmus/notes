from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.urls import reverse

from notes.doa import validate_ownership_notes, validate_ownership_note, search_notes, search_notes_trash
from notes.file_response_provider import notes2txtzip_response, notes2pdfzip_response, render_markdown
from notes.forms import SelectNotesForm, NoteForm
from notes.models import Note
from notes.user_profiles import regular_context, trash_context


@login_required
def trash(request):
    # Create form
    notes = Note.objects.filter(notebook__owner=request.user, trash=True).order_by('id')

    if request.method != 'POST':
        form = SelectNotesForm()
        form.set_choices(notes)
    else:
        form = SelectNotesForm(data=request.POST)
        form.set_choices(notes)

        if form.is_valid():
            # Collect valid nodes
            valid_notes = validate_ownership_notes(request.user, form.cleaned_data['picked'])

            if len(valid_notes) > 0:
                # Download
                if 'downloadtxts' in request.POST:
                    return notes2txtzip_response(valid_notes, 'notes-trash-all')

                # Download
                if 'downloadpdfs' in request.POST:
                    return notes2pdfzip_response(valid_notes, 'notes-trash-all')

                # Move
                if 'restore' in request.POST:
                    note_ids = ','.join([str(note.id) for note in valid_notes])
                    return HttpResponseRedirect(reverse('trash:restore-notes', kwargs={'note_ids': note_ids}))

                # Delete
                if 'delete' in request.POST:
                    note_ids = ','.join([str(note.id) for note in valid_notes])
                    return HttpResponseRedirect(reverse('trash:permanent-delete-notes', kwargs={'note_ids': note_ids}))

    # Render
    context = trash_context(request.user)
    context['form'] = form
    context['notes'] = notes
    return render(request, 'view_trash.html', context)


@login_required
def view_note(request, note_id):
    # Validate note
    current_note = validate_ownership_note(request.user, note_id)

    # Render
    current_note.rendered_content = render_markdown(current_note.content)

    context = trash_context(request.user)
    context['current_note'] = current_note
    return render(request, 'view_trash_note.html', context)


@login_required
def delete_notes(request, note_ids):
    # Validate notes
    note_id_array = note_ids.split(',')
    notes = validate_ownership_notes(request.user, note_id_array)

    if request.method == 'POST':
        for note in notes:
            note.delete()
        return redirect('trash:trash')

    # Render
    context = trash_context(request.user)
    context['notes'] = notes
    context['current_note_ids'] = note_ids
    return render(request, 'permanent_delete_notes.html', context)


@login_required
def delete_note(request, note_id):
    # Validate note
    note = validate_ownership_note(request.user, note_id)

    if request.method == 'POST':
        note.delete()
        return redirect('trash:trash')

    # Render
    context = trash_context(request.user)
    context['current_note'] = note
    return render(request, 'permanent_delete_note.html', context)


@login_required
def delete_all_notes(request):
    notes = Note.objects.filter(notebook__owner=request.user, trash=True)

    if request.method == 'POST':
        for note in notes:
            note.delete()
        return redirect('trash:trash')

    # Render
    context = trash_context(request.user)
    context['notes'] = notes
    context['current_note_ids'] = ','.join([str(note.id) for note in notes])
    return render(request, 'delete_all_notes.html', context)


@login_required
def restore_note(request, note_id):
    # Validate note
    note = validate_ownership_note(request.user, note_id)

    if request.method == 'POST':
        note.trash = False
        note.save()
        return redirect('trash:trash')

    # Render
    context = trash_context(request.user)
    context['current_note'] = note
    return render(request, 'restore_note.html', context)


@login_required
def restore_notes(request, note_ids):
    # Validate notes
    note_id_array = note_ids.split(',')
    notes = validate_ownership_notes(request.user, note_id_array)

    if request.method == 'POST':
        for note in notes:
            note.trash = False
            note.save()
        return redirect('trash:trash')

    # Render
    context = trash_context(request.user)
    context['notes'] = notes
    context['current_note_ids'] = note_ids
    return render(request, 'restore_notes.html', context)


@login_required
def restore_all_notes(request):
    notes = Note.objects.filter(notebook__owner=request.user, trash=True)

    if request.method == 'POST':
        for note in notes:
            note.trash = False
            note.save()
        return redirect('trash:trash')

    # Render
    context = trash_context(request.user)
    context['notes'] = notes
    context['current_note_ids'] = ','.join([str(note.id) for note in notes])
    return render(request, 'restore_all_notes.html', context)


@login_required
def download_trash(request, filetype):
    notes = Note.objects.filter(notebook__owner=request.user, trash=True)

    # Return file
    if filetype == 'txt':
        return notes2txtzip_response(notes)
    elif filetype == 'pdf':
        return notes2pdfzip_response(notes)
    else:
        raise Http404('Invalid filetype.')


@login_required
def search(request):
    if request.method != 'POST':
        return redirect('trash:trash')

    # Render
    query = request.POST['query']

    context = regular_context(request.user)
    context['query'] = query
    context['notes'] = search_notes_trash(request.user, query)
    return render(request, 'search_trash.html', context)
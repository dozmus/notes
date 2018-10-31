import random
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.timezone import utc

from notes.doa import notebooks, notes, validate_ownership_note
from notes.file_response_provider import render_markdown, note2txt_response, note2pdf_response
from notes.models import UserProfile, Note
from notes.user_profiles import regular_context
from share.forms import SharableLinkForm, EditSharableLinkForm, SharedNoteForm
from share.models import SharableLink


@login_required
def share_note(request, note_id):
    # Validate note
    current_note = validate_ownership_note(request.user, note_id)

    # Render
    sharable_links = current_note.sharablelink_set.all()

    for link in sharable_links:
        args = {'note_id': current_note.id, 'code': link.code}
        link.full_url = request.build_absolute_uri(reverse('share:view-note', kwargs=args))

    current_note.rendered_content = render_markdown(current_note.content)

    context = regular_context(request.user)
    context['current_note'] = current_note
    context['sharable_links'] = sharable_links
    return render(request, 'share_note.html', context)


@login_required
def new_share_link(request, note_id):
    # Validate note
    current_note = validate_ownership_note(request.user, note_id)

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
    context = regular_context(request.user)
    context['form'] = form
    context['current_note'] = current_note
    return render(request, 'new_share_link.html', context)


@login_required
def edit_share_link(request, note_id, code):
    # Validate note
    current_note = validate_ownership_note(request.user, note_id)
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
    context = regular_context(request.user)
    context['form'] = form
    context['current_note'] = current_note
    context['code'] = code
    return render(request, 'edit_share_link.html', context)


@login_required
def delete_share_link(request, note_id, code):
    # Validate note
    note, sharable_link = validate_ownership_shared_note(request, note_id, code, False)

    if request.method == 'POST':
        sharable_link.delete()
        return redirect('home')

    # Render
    context = regular_context(request.user)
    context['current_note'] = note
    context['code'] = code
    return render(request, 'delete_share_link.html', context)


def edit_shared_note(request, note_id, code):
    # Validate note
    note, sharable_link = validate_ownership_shared_note(request, note_id, code)

    # Create form
    if request.method != 'POST':
        form = SharedNoteForm(data={
            'title': note.title,
            'content': note.content,
            'tags': note.tags
        })
    else:
        form = SharedNoteForm(data=request.POST)

        if form.is_valid() and sharable_link.permissions == 'read+write':
            note.title = form.cleaned_data['title']
            note.content = form.cleaned_data['content']
            note.tags = form.cleaned_data['tags']
            note.save()
            return HttpResponseRedirect(reverse('share:view-note', kwargs={'note_id': note_id, 'code': code}))

    # Render
    context = regular_context(request.user)
    context['form'] = form
    context['current_note'] = note
    context['code'] = code
    return render(request, 'edit_shared_note.html', context)


def delete_shared_note(request, note_id, code):
    # Validate note
    note, sharable_link = validate_ownership_shared_note(request, note_id, code)

    if request.method == 'POST' and sharable_link.permissions == 'read+write':
        note.delete()
        return redirect('home')

    # Render
    context = regular_context(request.user)
    context['current_note'] = note
    context['code'] = code
    return render(request, 'delete_shared_note.html', context)


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

    # Render
    note.rendered_content = render_markdown(note.content)

    context = regular_context(request.user)
    context['current_note'] = note
    context['code'] = sharable_link.code
    context['permissions'] = sharable_link.permissions
    return render(request, 'view_shared_note.html', context)


def validate_ownership_shared_note(request, note_id, code, check_expiry_date=True):
    # Get sharable link and note
    try:
        note = Note.objects.filter(id=note_id).get()
        sharable_link = SharableLink.objects.filter(note_id=note_id).filter(code=code).get()
    except:
        raise Http404('Note does not exist.')

    # Check expiry date
    if check_expiry_date and sharable_link.expiry_date < utc.localize(datetime.now()):
        raise Http404('This share link has expired.')
    return note, sharable_link

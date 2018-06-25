from io import BytesIO
from typing import List, Tuple
from zipfile import ZipFile

from django.http import HttpResponse, HttpRequest
from easy_pdf.rendering import render_to_pdf_response, render_to_pdf
from markdown2 import Markdown

from notes.models import Note, Notebook


def note2txt_response(note: Note) -> HttpResponse:
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="note-%s.txt"' % str(note.id)

    # Write text
    data = 'Title: ' + note.title + '\r\n\r\nContent:\r\n' + note.content
    response.write(data)
    return response


def note2pdf_response(request: HttpRequest, note: Note) -> HttpResponse:
    # Source: https://stackoverflow.com/a/48697734
    template = 'note2pdf.html'
    note.rendered_content = render_markdown(note.content)
    context = {'note': note}
    response = render_to_pdf_response(request, template, context)
    response['Content-Disposition'] = 'attachment; filename="note-%s.pdf"' % str(note.id)
    return response


def notebook2txtzip(notebook: Notebook) -> HttpResponse:
    notes = Note.objects.filter(notebook_id=notebook.id).order_by('id')
    filename = 'notebook-%s.zip' % notebook.title
    return notes2txtzip_response(notes, filename)


def notebook2pdfzip(notebook: Notebook) -> HttpResponse:
    notes = Note.objects.filter(notebook_id=notebook.id).order_by('id')
    filename = 'notebook-%s.zip' % notebook.title
    return notes2pdfzip_response(notes, filename)


def notes2txtzip_response(notes: List[Note], filename: str='notes-partial.zip') -> HttpResponse:
    # Create contents
    files = []

    for note in notes:
        fname = 'note-%s.txt' % str(note.id)
        data = 'Title: ' + note.title + '\r\n\r\nContent:\r\n' + note.content
        files.append((fname, data), )

    # Return zip
    return zip_response(files, filename)


def notes2pdfzip_response(notes: List[Note], filename: str='notes-partial.zip') -> HttpResponse:
    # Create contents
    files = []

    for note in notes:
        fname = 'note-%s.pdf' % str(note.id)
        pdf = note2pdf(note)
        files.append((fname, pdf), )

    # Return zip
    return zip_response(files, filename)


def zip_response(files: List[Tuple[str, str or bytes]], filename: str) -> HttpResponse:
    """
    Returns a HttpResponse for downloading a zip file with the argument files and names.
    :param files: a list of tuples, whose first entry is filename and second content (a string or bytes).
    :param filename: the zip file name
    """
    # Source: https://chase-seibert.github.io/blog/2010/07/23/django-zip-files-create-dynamic-in-memory-archives-with-pythons-zipfile.html
    # Create ZIP
    in_memory = BytesIO()
    zip = ZipFile(in_memory, 'a')

    for file in files:
        data = file[1].encode('utf-8') if type(file[1]) == '<class \'str\'>' else file[1]
        zip.writestr(file[0], data)

    # Fix for Linux zip files read in Windows
    for file in zip.filelist:
        file.create_system = 0

    zip.close()

    # Create response
    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename

    # Write data
    in_memory.seek(0)
    response.write(in_memory.read())
    return response


def note2pdf(note: Note):
    template = 'note2pdf.html'
    note.rendered_content = render_markdown(note.content)
    context = {'note': note}
    return render_to_pdf(template, context)


def render_markdown(raw: str) -> str:
    """
    Returns the argument raw markdown as its equivalent HTML, with the 'fenced-code-blocks' option.
    :param raw: raw markdown
    """
    return Markdown(extras=['fenced-code-blocks']).convert(raw)

from io import BytesIO
from zipfile import ZipFile

from django.http import HttpResponse
from easy_pdf.rendering import render_to_pdf_response, render_to_pdf
from markdown2 import Markdown

from notes.models import Note


def note2txt_response(note):
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="note-%s.txt"' % str(note.id)

    # Write text
    data = 'Title: ' + note.title + '\r\n\r\nContent:\r\n' + note.content
    response.write(data)
    return response


def note2pdf_response(request, note):
    # Source: https://stackoverflow.com/a/48697734
    template = 'note2pdf.html'
    note.rendered_content = render_markdown(note.content)
    context = {'note': note}
    response = render_to_pdf_response(request, template, context)
    response['Content-Disposition'] = 'attachment; filename="note-%s.pdf"' % str(note.id)
    return response


def notebook2txtzip(notebook):
    notes = Note.objects.filter(notebook_id=notebook.id).order_by('id')
    filename = 'notebook-%s.zip' % notebook.title
    return notes2txtzip_response(notes, filename)


def notebook2pdfzip(notebook):
    notes = Note.objects.filter(notebook_id=notebook.id).order_by('id')
    filename = 'notebook-%s.zip' % notebook.title
    return notes2pdfzip_response(notes, filename)


def notes2txtzip_response(notes, filename='notes-partial.zip'):
    # Create contents
    files = []

    for note in notes:
        fname = 'note-%s.txt' % str(note.id)
        data = 'Title: ' + note.title + '\r\n\r\nContent:\r\n' + note.content
        files.append((fname, data), )

    # Return zip
    return zip_response(files, filename)


def notes2pdfzip_response(notes, filename='notes-partial.zip'):
    # Create contents
    files = []

    for note in notes:
        fname = 'note-%s.pdf' % str(note.id)
        pdf = note2pdf(note)
        files.append((fname, pdf), )

    # Return zip
    return zip_response(files, filename)


def zip_response(files, filename):
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


def note2pdf(note):
    template = 'note2pdf.html'
    note.rendered_content = render_markdown(note.content)
    context = {'note': note}
    return render_to_pdf(template, context)


def render_markdown(raw):
    return Markdown(extras=['fenced-code-blocks']).convert(raw)

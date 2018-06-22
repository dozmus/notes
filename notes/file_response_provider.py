from io import BytesIO
from zipfile import ZipFile

from django.http import HttpResponse
from easy_pdf.rendering import render_to_pdf_response

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
    context = {'note': note}
    response = render_to_pdf_response(request, template, context)
    response['Content-Disposition'] = 'attachment; filename="note-%s.pdf"' % str(note.id)
    return response


def notebook2zip_response(notebook):
    # Source: https://chase-seibert.github.io/blog/2010/07/23/django-zip-files-create-dynamic-in-memory-archives-with-pythons-zipfile.html
    # Create ZIP
    in_memory = BytesIO()
    zip = ZipFile(in_memory, 'a')

    for note in Note.objects.filter(notebook_id=notebook.id).order_by('id'):
        filename = 'note-%s.txt' % str(note.id)
        data = 'Title: ' + note.title + '\r\n\r\nContent:\r\n' + note.content
        zip.writestr(filename, data.encode('utf-8'))

    # Fix for Linux zip files read in Windows
    for file in zip.filelist:
        file.create_system = 0

    zip.close()

    # Create response
    response = HttpResponse(content_type="application/zip")
    response["Content-Disposition"] = "attachment; filename=notebook-%s.zip" % str(notebook.id)

    # Write data
    in_memory.seek(0)
    response.write(in_memory.read())
    return response

from django.http import HttpResponse
from easy_pdf.rendering import render_to_pdf_response


def note2txt_response(note):
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="note-%s.txt"' % str(note.id)

    # Write text
    data = 'Title: ' + note.title + '\r\n\r\nContent:\r\n' + note.content
    response.write(data)
    return response


def note2pdf_response(request, note):
    template = 'note2pdf.html'
    context = {'note': note}
    response = render_to_pdf_response(request, template, context)
    response['Content-Disposition'] = 'attachment; filename="note-%s.pdf"' % str(note.id)
    return response

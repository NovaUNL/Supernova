from django.shortcuts import render, get_object_or_404

from documents.models import Document
from kleep.views import build_base_context


def document(request, document_id):
    context = build_base_context(request)
    document = get_object_or_404(Document, id=document_id)
    title = document.title
    context['title'] = title
    context['document'] = document
    context['sub_nav'] = [{'name': 'Documentos', 'url': '#'},
                          {'name': title, 'url': '#'}]
    return render(request, 'documents/document.html', context)

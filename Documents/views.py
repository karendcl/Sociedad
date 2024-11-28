from django.shortcuts import render
from django.http import HttpResponse
from .models import ApprovedDocuments, PendingDocuments

# Create your views here.

def index(request):
    return render(request, 'base/main.html')

def search(request):
    documents = ApprovedDocuments.objects.all()
    if request.method == 'POST':
        title = request.POST['title']
        kw = request.POST['keyword']

        all_documents = documents
        d = []

        for document in all_documents:
            if title != '' and title not in document.name:
                continue
            if kw != '' and kw not in document.text:
                continue
            d.append(document)

        documents = d
    return render(request, 'docs/search.html', {'docs': documents})

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
        kw = request.POST['kw']

        all_documents = documents
        d = []

        for document in all_documents:
            if title != '' and title in document.name:
                d.append(document)
            if kw != '' and kw in document.text:
                d.append(document)
        print(d)
        documents = d
    return render(request, 'docs/search.html', {'docs': documents})

def insert(request):
    if request.method == 'POST':
        pic = request.FILES['file']
        title = request.POST['title']
        text = 'Pruebita'
        doc = PendingDocuments.objects.create(image=pic, name=title, text=text)
        doc.save()

        return render(request, 'docs/insert.html')
    return render(request, 'docs/insert.html')

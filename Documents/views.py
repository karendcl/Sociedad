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
        if title == '' and kw == '':
            return render(request, 'docs/search.html', {'docs': documents})

        for document in all_documents:
            if title != '' and title in document.name:
                d.append(document)
            if kw != '' and kw in document.text:
                d.append(document)

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

def view_doc(request, doc_id):
    doc = ApprovedDocuments.objects.get(pk=doc_id)
    return render(request, 'docs/view.html', {'document': doc})

def pending(request):
    posts = PendingDocuments.objects.all()
    return render(request, 'docs/pending.html', {'posts': posts})

def edit(request, doc_id):
    doc = PendingDocuments.objects.get(pk=doc_id)
    if request.method == 'POST':
        try:
            name = request.POST['title']
            if name == '':
                raise Exception
            doc.name = name
        except:
            pass

        try:
            text = request.POST['text']
            if text == '':
                raise Exception
            doc.text = text
        except:
            pass

        #add it to approved documents
        doc.save()
        ApprovedDocuments.objects.create(image=doc.image, name=doc.name, text=doc.text)
        doc.delete()

        return render(request, 'docs/pending.html', {'posts': PendingDocuments.objects.all()})
    return render(request, 'docs/review.html', {'document': doc})

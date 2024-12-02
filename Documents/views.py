from django.shortcuts import render
from django.http import HttpResponse
from .models import ApprovedDocuments, PendingDocuments


from pathlib import Path
import os, sys
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(os.path.join(BASE_DIR, 'model'))

import segmentation as segmentation
import ocr as ocr
import xml_generator as xml_generator


# Create your views here.

def index(request):
    return render(request, 'base/main.html')

def search(request):
    documents = ApprovedDocuments.objects.all()
    print(documents)
    try:
        title = request.POST['title']
    except:
        return render(request, 'docs/search.html', {'docs': documents})

    if request.method == 'POST':

        title = request.POST['title']
        kw = request.POST['kw']

        print(title)
        print(kw)

        all_documents = documents
        d = []
        if title == '' and kw == '' or (not title and not kw):
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

        img_url = doc.image.url
        urls = segmentation.cropped_img_path(img_url, BASE_DIR)

        predicted_text: [str] = ocr.predict_text(BASE_DIR)

        # join the text by \n
        txt = '\n'.join(predicted_text)
        doc.text = txt

        xml = xml_generator.generate_xml(img_url, predicted_text, title)

        doc.xml_file = xml

        # remove the images
        for url in urls:
            os.remove(url)

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

        try:
            xml = request.POST['xml_text']
            if xml == '':
                raise Exception
            doc.xml_file = xml
        except:
            pass

        #add it to approved documents
        doc.save()
        ApprovedDocuments.objects.create(image=doc.image, name=doc.name, text=doc.text, xml_file=doc.xml_file)
        doc.delete()

        return render(request, 'docs/pending.html', {'posts': PendingDocuments.objects.all()})
    return render(request, 'docs/review.html', {'document': doc})

def download_xml(request, doc_id):
    doc = ApprovedDocuments.objects.get(pk=doc_id)
    xml = doc.xml_file

    response = HttpResponse(xml, content_type='text/xml')
    response['Content-Disposition'] = f'attachment; filename="{doc.name}.xml"'
    return response
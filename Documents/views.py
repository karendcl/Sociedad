from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import ApprovedDocuments, PendingDocuments
from django.views.generic import ListView
from django.core.paginator import Paginator
from Users.models import Profile
from django.contrib.auth.models import User
from django.contrib import messages



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

def search(request, from_fav=False):
    documents = ApprovedDocuments.objects.all()
    pagination_size = 4

    try:
        user = User.objects.get(username=request.user.username)
        profile = Profile.objects.get(user=user)
        fav_docs = profile.fav_docs.all()
    except:
        fav_docs = None

    if not from_fav:
        try:
            title = request.POST['title']
        except:
            if request.session.get('filtered', None):
                documents = [ApprovedDocuments.objects.get(pk=i) for i in request.session['filtered']]
            paginator = Paginator(documents, pagination_size)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            return render(request, 'docs/search.html', {'docs': documents, 'page_obj': page_obj,
                                                        'fav_docs': fav_docs})

    if request.method == 'POST':

        title = request.POST['title']
        kw = request.POST['kw']

        d = []
        if title == '' and kw == '' or (not title and not kw):

            request.session['filtered'] = None
            paginator = Paginator(documents, pagination_size)
            print(documents)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            return render(request, 'docs/search.html', {'docs':documents, 'page_obj': page_obj,
                                                        'fav_docs': fav_docs})

        filtered = [i for i in documents if (title != '' and title in i.name) or (kw != '' and kw in i.text)]

        # save in the browser the ids of the documents
        request.session['filtered'] = [i.id for i in filtered]

        documents = filtered
        paginator = Paginator(documents, pagination_size)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'docs/search.html', {'docs': documents, 'page_obj': page_obj,
                                                    'fav_docs': fav_docs})

    if from_fav:
        if request.session.get('filtered', None):
            documents = [ApprovedDocuments.objects.get(pk=i) for i in request.session['filtered']]
        paginator = Paginator(documents, pagination_size)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'docs/search.html', {'docs': documents, 'page_obj': page_obj,
                                                    'fav_docs': fav_docs})

def insert(request):
    if request.method == 'POST':
        try:
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

            # # remove the images
            for url in urls:
                os.remove(url)

            doc.save()
            messages.success(request, 'Document uploaded successfully')
        except:
            messages.error(request, 'There was an error')


        return render(request, 'docs/insert.html')
    return render(request, 'docs/insert.html')

def view_doc(request, doc_id):
    doc = ApprovedDocuments.objects.get(pk=doc_id)
    return render(request, 'docs/view.html', {'document': doc, 'page':request.GET.get('page')})

def pending(request):
    posts = PendingDocuments.objects.all()
    # add the pagination
    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'docs/pending.html', {'posts': posts, 'page_obj': page_obj})

def edit(request, doc_id):
    doc = PendingDocuments.objects.get(pk=doc_id)

    if request.method == 'POST':
        try:
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

            xml = xml_generator.generate_xml(doc.image.url, doc.text.split('\n'), doc.name)
            doc.xml_file = xml

            #add it to approved documents
            doc.save()
            ApprovedDocuments.objects.create(image=doc.image, name=doc.name, text=doc.text, xml_file=doc.xml_file)
            doc.delete()

            messages.success(request, 'Document edited successfully')

            # pagination
            posts = PendingDocuments.objects.all()
            paginator = Paginator(posts, 15)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            return redirect('pending', permanent=True)
        except:
            messages.error(request, 'There was an error')
            return redirect('pending', permanent=True)


    return render(request, 'docs/review.html', {'document': doc, 'page': request.GET.get('page')})

def download_xml(request, doc_id):
    doc = ApprovedDocuments.objects.get(pk=doc_id)
    xml = doc.xml_file

    response = HttpResponse(xml, content_type='text/xml')
    response['Content-Disposition'] = f'attachment; filename="{doc.name}.xml"'
    return response

def add_fav(request, doc_id):
    doc = ApprovedDocuments.objects.get(pk=doc_id)
    user = User.objects.get(username=request.user.username)
    profile = Profile.objects.get(user=user)
#     ADD RELATIONSHIP BETWEEN PROFILE AND DOC
    profile.fav_docs.add(doc)
    return search(request, from_fav=True)

def remove_fav(request, doc_id):
    doc = ApprovedDocuments.objects.get(pk=doc_id)
    user = User.objects.get(username=request.user.username)
    profile = Profile.objects.get(user=user)
    profile.fav_docs.remove(doc)
    return search(request, from_fav=True)

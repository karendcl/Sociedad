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
    pagination_size = 5

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
        date = request.POST['date']
        author = request.POST['author']
        place = request.POST['place']
        type_doc = request.POST['type']

        type_map = {
            '0': '',
            '1': 'Ordinaria',
            '2': 'Extraordinaria',
            '3': ''}

        type_doc = type_map[type_doc]

        ordered = request.POST['order-by']

        filtered = [i for i in documents if
                    (title == '' or title in i.name) and
                    (kw == '' or kw in i.text) and
                    (date == '' or date in i.xml_file) and
                    (author == '' or author in i.xml_file) and
                    (place == '' or place in i.xml_file) and
                    (type_doc == '' or type_doc in i.xml_file)]
        print('filtering by: \n title:', title, '\n kw:', kw, '\n date:', date, '\n author:', author, '\n place:', place, '\n type:', type_doc)

        if ordered == '1':
            filtered = sorted(filtered, key=lambda x: x.fecha)
        elif ordered == '2':
            filtered = sorted(filtered, key=lambda x: x.fecha, reverse=True)
        elif ordered == '3':
            filtered = sorted(filtered, key=lambda x: x.name.upper())
        elif ordered == '4':
            filtered = sorted(filtered, key=lambda x: x.name.upper(), reverse=True)

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
            # pic = request.FILES['file']

            # select all the images inserted
            pics = request.FILES.getlist('file')
            print(pics)
            pic = pics[0]


            title = request.POST['title']
            text = 'Pruebita'

            doc = PendingDocuments.objects.create(image=pic, name=title, text=text)
            doc.save()

            img_url = doc.image.url
            urls, raw = segmentation.cropped_img_path(img_url, BASE_DIR)
            print(urls)

            predicted_text: [str] = ocr.predict_text(BASE_DIR, raw)

            # join the text by \n
            txt = '\n'.join(predicted_text)
            doc.text = txt

            xml = xml_generator.generate_xml(img_url, predicted_text, title)

            doc.xml_file = xml

            # # remove the images
            for url in urls:
                os.remove(url)


            doc.save()
            messages.success(request, 'Documento insertado')
        except Exception as e:
            messages.error(request, f'Ocurrio un error: {e}')


        return render(request, 'docs/insert.html')
    return render(request, 'docs/insert.html')

def view_doc(request, doc_id):
    doc = ApprovedDocuments.objects.get(pk=doc_id)
    return render(request, 'docs/view.html', {'document': doc, 'page':request.GET.get('page'), 'from_fav': False})

def view_doc_f(request, doc_id):
    doc = ApprovedDocuments.objects.get(pk=doc_id)
    return render(request, 'docs/view.html', {'document': doc, 'page':request.GET.get('page'), 'from_fav': True})

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

            messages.success(request, 'Documento aceptado')

            # pagination
            posts = PendingDocuments.objects.all()
            paginator = Paginator(posts, 15)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            return redirect('pending', permanent=True)
        except Exception as e:
            messages.error(request, f'Ocurrio un error: {e}')
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

def favorites(request):
    user = User.objects.get(username=request.user.username)
    profile = Profile.objects.get(user=user)
    fav_docs = profile.fav_docs.all()

    # pagination
    paginator = Paginator(fav_docs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'docs/favs.html', {'docs': fav_docs, 'page_obj': page_obj})

def delete(request, doc_id):
    doc = PendingDocuments.objects.get(pk=doc_id)
    doc.delete()
    # message
    messages.success(request, 'Documento rechazado')
    return redirect('pending', permanent=True)

def clean(request):
    documents = ApprovedDocuments.objects.all()
    pagination_size = 4

    try:
        user = User.objects.get(username=request.user.username)
        profile = Profile.objects.get(user=user)
        fav_docs = profile.fav_docs.all()
    except:
        fav_docs = None

    request.session['filtered'] = None

    paginator = Paginator(documents, pagination_size)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'docs/search.html', {'docs': documents, 'page_obj': page_obj,
                                                'fav_docs': fav_docs})

from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Page, Act
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
    return render(request, 'base/about.html')

def search(request, from_fav=False):
    # get all acts that are approved
    docs = Act.objects.all()
    documents = [doc for doc in docs if doc.approved]
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
                documents = [Act.objects.get(pk=i) for i in request.session['filtered']]
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
                    (title == '' or title in i.title) and
                    (kw == '' or kw in i.xml_file) and
                    (date == '' or date in str(i.year)) and
                    (author == '' or author in i.author) and
                    (place == '' or place in i.place) and
                    (type_doc == '' or type_doc in i.type)]
        print('filtering by: \n title:', title, '\n kw:', kw, '\n date:', date, '\n author:', author, '\n place:', place, '\n type:', type_doc)


        if ordered == '1':
            filtered = sorted(filtered, key=lambda x: x.year)
        elif ordered == '2':
            filtered = sorted(filtered, key=lambda x: x.year, reverse=True)
        elif ordered == '3':
            filtered = sorted(filtered, key=lambda x: x.title.upper())
        elif ordered == '4':
            filtered = sorted(filtered, key=lambda x: x.title.upper(), reverse=True)

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
            documents = [Act.objects.get(pk=i) for i in request.session['filtered']]
        paginator = Paginator(documents, pagination_size)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'docs/search.html', {'docs': documents, 'page_obj': page_obj,
                                                    'fav_docs': fav_docs})

def insert(request):
    if request.method == 'POST':
        try:
            # select all the images inserted
            pics = request.FILES.getlist('file')
            print(pics)

            title = request.POST['title']
            date = request.POST['date']
            author = request.POST['author']
            place = request.POST['place']
            type_doc = request.POST['type']


            pages = []
            image_urls = []
            for pic in pics:
                text = 'Pruebita'

                page = Page.objects.create(image=pic, text=text)
                page.save()

                img_url = page.image.url
                urls, raw = segmentation.cropped_img_path(img_url, BASE_DIR)
                print(urls)

                predicted_text: [str] = ocr.predict_text(BASE_DIR, raw)

                # join the text by \n
                txt = '\n'.join(predicted_text)
                page.text = txt
                page.save()
                pages.append(page)
                image_urls.append(img_url)

                # # remove the images
                for url in urls:
                    os.remove(url)


            predicted_text = [page.text for page in pages]
            xml = xml_generator.generate_xml(image_urls, predicted_text, title,
                                             author, date, place, type_doc)

            doc = Act.objects.create(title=title,
                                     year=date,
                                     author=author,
                                     place=place,
                                     type=type_doc,
                                     xml_file=xml,
                                     approved=False)
            doc.pages.set(pages)
            doc.save()
            messages.success(request, 'Documento insertado')
        except Exception as e:
            messages.error(request, f'Ocurrio un error: {e}')


        return render(request, 'docs/insert.html')
    return render(request, 'docs/insert.html')

def view_doc(request, doc_id):
    doc = Act.objects.get(pk=doc_id)
    act_page = request.GET.get('act_page')
    if act_page:
        act_page = Page.objects.get(pk=act_page)
    else:
        act_page = doc.pages.all()[0]

    has_next, has_prev, page, act = determine_nex_prev(doc_id, act_page.id, 0)

    return render(request, 'docs/view.html', {'document': doc, 'page':request.GET.get('page'),
                                              'from_fav': False, 'act_page': act_page,
                                              'has_next': has_next,
                                              'has_prev': has_prev})

def view_doc_f(request, doc_id):
    doc = Act.objects.get(pk=doc_id)
    act_page = request.GET.get('act_page')
    if act_page:
        act_page = Page.objects.get(pk=act_page)
    else:
        act_page = doc.pages.all()[0]

    has_next, has_prev, page, act = determine_nex_prev(doc_id, act_page.id, 0)

    return render(request, 'docs/view.html', {'document': doc, 'page': request.GET.get('page'),
                                              'from_fav': True, 'act_page': act_page,
                                              'has_next': has_next,
                                              'has_prev': has_prev})
def pending(request):
    posts = Act.objects.all()
    posts = [post for post in posts if not post.approved]
    # add the pagination
    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    request.session['act_page'] = None
    return render(request, 'docs/pending.html', {'posts': posts, 'page_obj': page_obj})



def save_page_changes(request, page_id):
    try:
        act_id = request.GET.get('act_id')
        page = Page.objects.get(pk=page_id)
        text = request.POST['text']
        page.text = text
        page.save()

        messages.success(request, 'Página guardada')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    request.session['act_page'] = page_id
    # return edit(request, act_id)
    return redirect('edit', doc_id=act_id)

def edit(request, doc_id):
    doc = Act.objects.get(pk=doc_id)
    index = request.GET.get('act_page') or request.session['act_page']
    if index:
        page = Page.objects.get(pk=index)
    else:
        page = doc.pages.all()[0]
        index = page.id


    if request.method == 'POST':
        try:
            try:
                name = request.POST['title']
                if name == '':
                    raise Exception
                doc.title = name
            except:
                pass

            try:
                author = request.POST['author']
                if author == '':
                    raise Exception
                doc.author = author
            except:
                pass

            try:
                place = request.POST['place']
                if place == '':
                    raise Exception
                doc.place = place
            except:
                pass

            try:
                date = request.POST['date']
                if date == '':
                    raise Exception
                doc.year = date

            except:
                pass

            try:
                type_doc = request.POST['type']
                doc.type = type_doc
            except:
                pass

            doc.save()


            img_urls = [page.image.url for page in doc.pages.all()]
            text = [page.text for page in doc.pages.all()]
            xml = xml_generator.generate_xml(img_urls, text, doc.title,
                                             doc.author, doc.year, doc.place, doc.type)
            doc.xml_file = xml
            doc.approved = True
            #add it to approved documents
            doc.save()

            messages.success(request, 'Documento aceptado')

            # pagination

            # get acts that are not approved by filtering by its boolean field 'approved'
            posts = Act.objects.all()
            posts = [post for post in posts if not post.approved]

            paginator = Paginator(posts, 15)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            return redirect('pending', permanent=True)
        except Exception as e:
            messages.error(request, f'Ocurrio un error: {e}')
            return redirect('pending', permanent=True)

    has_next, has_prev, page, act = determine_nex_prev(doc_id, index, 0)
    return render(request, 'docs/review.html', {'document': doc,
                                                'page': request.GET.get('page'),
                                                'act_page': page,
                                                'has_next': has_next,
                                                'has_prev': has_prev,
                                                })

def download_xml(request, doc_id):
    doc = Act.objects.get(pk=doc_id)
    xml = doc.xml_file

    response = HttpResponse(xml, content_type='text/xml')
    response['Content-Disposition'] = f'attachment; filename="{doc.title}.xml"'
    return response

def add_fav(request, doc_id):
    doc = Act.objects.get(pk=doc_id)
    user = User.objects.get(username=request.user.username)
    profile = Profile.objects.get(user=user)
#     ADD RELATIONSHIP BETWEEN PROFILE AND DOC
    profile.fav_docs.add(doc)
    return search(request, from_fav=True)

def remove_fav(request, doc_id):
    doc = Act.objects.get(pk=doc_id)
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
    doc = Act.objects.get(pk=doc_id)
    doc.delete()
    # message
    messages.success(request, 'Documento rechazado')
    return redirect('pending', permanent=True)

def clean(request):
    documents = Act.objects.all()
    documents = [doc for doc in documents if doc.approved]
    pagination_size = 5

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


def determine_nex_prev(act_id, page_id, change):
    change = int(change)
    action = {0:0, 1:1, 2:-1}
    change = action[change]

    act = Act.objects.get(pk=act_id)
    # get position of page_id in act.pages
    pages = act.pages.all()
    ind = [i for i in range(pages.count()) if pages[i].id == page_id]
    ind = ind[0]
    new_ind = ind + change

    if new_ind == pages.count():
        new_ind = ind
        has_next = False
    else:
        has_next = new_ind != pages.count() - 1

    if new_ind == -1:
        new_ind = ind
        has_prev = False
    else:
        has_prev = new_ind != 0

    page = pages[new_ind]

    return has_next, has_prev, page, act

def change_page(request, act_id, page_id, change):
    has_next, has_prev, page, act = determine_nex_prev(act_id, page_id, change)

    context = {'document': act,
               'page': request.GET.get('page'),
               'act_page': page,
               'has_next': has_next,
               'has_prev': has_prev}

    return render(request, 'docs/review.html', context)

def change_view(request, act_id, page_id, change):
    has_next, has_prev, page, act = determine_nex_prev(act_id, page_id, change)

    context = {'document': act,
               'page': request.GET.get('page'),
               'act_page': page,
               'has_next': has_next,
               'has_prev': has_prev,
               'from_fav': False}

    return render(request, 'docs/view.html', context)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.search, name='index'),
    path('search/', views.search, name='search'),
    path('insert/', views.insert, name='insert'),
    #ex doc/5
    path('doc/<int:doc_id>/', views.view_doc, name='doc'),
    path('pending/', views.pending, name='pending'),
    path('edit/<int:doc_id>/', views.edit, name='edit'),
    path('download/<int:doc_id>/', views.download_xml, name='download'),
    path('add_fav/<int:doc_id>/', views.add_fav, name='add_fav'),
    path('rem_fav/<int:doc_id>/', views.remove_fav, name='remove_fav'),
]
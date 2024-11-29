from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('insert/', views.insert, name='insert'),
    #ex doc/5
    path('doc/<int:doc_id>/', views.view_doc, name='doc'),
    path('pending/', views.pending, name='pending'),
    path('edit/<int:doc_id>/', views.edit, name='edit'),
]
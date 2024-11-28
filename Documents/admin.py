from django.contrib import admin

# Register your models here.
from .models import ApprovedDocuments, PendingDocuments

admin.site.register(ApprovedDocuments)
admin.site.register(PendingDocuments)

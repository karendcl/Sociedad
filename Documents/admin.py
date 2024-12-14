from django.contrib import admin

# Register your models here.
from .models import ApprovedDocuments, PendingDocuments, Page, Act

admin.site.register(ApprovedDocuments)
admin.site.register(PendingDocuments)
admin.site.register(Page)
admin.site.register(Act)


from django.db import models
from django.contrib.auth.models import User
from Documents.models import ApprovedDocuments

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    active_role = models.CharField(max_length=200, default='user')
    fav_docs = models.ManyToManyField(ApprovedDocuments, blank=True, related_name='fav_docs')

    def __str__(self):
        return self.user.username



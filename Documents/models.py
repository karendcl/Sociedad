from django.db import models

# Create your models here.
class ApprovedDocuments(models.Model):
    image_url = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    text = models.TextField()

    def __str__(self):
        return self.name

class PendingDocuments(models.Model):
    image_url = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    text = models.TextField()

    def __str__(self):
        return self.name



from django.db import models

# Create your models here.
class ApprovedDocuments(models.Model):
    image = models.ImageField(upload_to='document_images/', default='document_images/default.jpg')
    name = models.CharField(max_length=200)
    text = models.TextField()

    def __str__(self):
        return self.name

class PendingDocuments(models.Model):
    image = models.ImageField(upload_to='document_images/', default='document_images/default.jpg')
    name = models.CharField(max_length=200)
    text = models.TextField()

    def __str__(self):
        return self.name



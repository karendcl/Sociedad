from django.db import models

# Create your models here.
class ApprovedDocuments(models.Model):
    image = models.ImageField(upload_to='document_images/', default='document_images/default.jpg')
    name = models.CharField(max_length=200)
    text = models.TextField()
    xml_file = models.TextField(default='')

    def __str__(self):
        return self.name

class PendingDocuments(models.Model):
    image = models.ImageField(upload_to='document_images/', default='document_images/default.jpg')
    name = models.CharField(max_length=200)
    text = models.TextField()
    xml_file = models.TextField(default='')

    def __str__(self):
        return self.name


class Page(models.Model):
    image = models.ImageField(upload_to='document_images/', default='document_images/default.jpg')
    text = models.TextField()

    def __str__(self):
        return self.text[:50] + '...'

class Act(models.Model):
    title = models.CharField(max_length=200)
    year = models.CharField(default='00/00/0000', max_length=10)
    author = models.CharField(max_length=200)
    place = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    xml_file = models.TextField()
    pages = models.ManyToManyField(Page)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.title



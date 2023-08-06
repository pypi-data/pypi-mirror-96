from django.conf import settings
from djangoldp.models import Model
from django.db import models


class Document(Model):
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class File(Model):
    original_url = models.CharField(max_length=255)
    content_type = models.CharField(max_length=255, default='None')
    stored_url = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.original_url
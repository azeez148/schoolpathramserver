import uuid

from django.conf import settings
from django.db import models


# Create your models here.

class NewsFeed(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='newsfeeds'
    )
    is_active = models.BooleanField(default=False)

class Image(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(blank=True, null=True, upload_to='images/')
    newsfeed = models.ForeignKey(NewsFeed, default=None, on_delete=models.CASCADE,)


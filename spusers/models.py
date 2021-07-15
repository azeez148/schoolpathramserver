import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _


# Enforce unique email addresses
# User._meta.get_field('email')._unique = True

# class SPUser(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)


class User(AbstractUser):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    username = models.CharField(max_length = 50, blank = False, null = True, unique = True)
    email = models.EmailField(_('email address'), unique = True)
#   native_name = models.CharField(max_length = 5)
    phone_no = models.CharField(max_length = 10)
    is_admin = models.BooleanField(default=False)
    
#   USERNAME_FIELD = 'email'
#   REQUIRED_FIELDS = ['username', 'email']
    # def __str__(self):
    #     return "{} {}".format(self.email)

class Image(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(blank=True, null=True, upload_to='images/')
    user = models.ForeignKey(User, default=None, on_delete=models.CASCADE,)
    created = models.DateTimeField(auto_now_add=True)
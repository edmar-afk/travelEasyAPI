from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
import os
# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.FileField(upload_to='user-profile/', validators=[FileExtensionValidator(allowed_extensions=['png', 'jpeg', 'jpg'])], blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    mobile_num = models.TextField(blank=True, null=True)
    
class Places(models.Model):
    name = models.TextField()
    image = models.FileField(upload_to='places/', validators=[FileExtensionValidator(allowed_extensions=['png', 'jpeg', 'jpg'])], blank=True)
    description = models.TextField()
    type = models.TextField()
    address = models.TextField(blank=True, null=True)
    status = models.TextField(null=True, blank=True)    
    def __str__(self):
        return self.name  # This will display the place name in the admin interface

class LikePlace(models.Model):
    user_like = models.ForeignKey(User, on_delete=models.CASCADE)
    place_name = models.ForeignKey(Places, on_delete=models.CASCADE)


class SubPlaces(models.Model):
    place = models.ForeignKey(Places, on_delete=models.CASCADE)
    name = models.TextField()
    image = models.FileField(upload_to='subplaces/', validators=[FileExtensionValidator(allowed_extensions=['png', 'jpeg', 'jpg'])], blank=True)
    description = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
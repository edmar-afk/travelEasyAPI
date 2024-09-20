from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
import os
# Create your models here.


class Places(models.Model):
    name = models.TextField()
    image = models.FileField(upload_to='places/', validators=[FileExtensionValidator(allowed_extensions=['png', 'jpeg', 'jpg'])], blank=True)
    description = models.TextField()
    type = models.TextField()
    address = models.TextField(blank=True, null=True)
    
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
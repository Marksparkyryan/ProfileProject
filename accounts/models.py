from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import os
import random

from cities_light.models import Country, City
from ckeditor.fields import RichTextField


class Profile(models.Model):
    """Model describing dditional info related to each user
    """
    def get_avatar():
        path = settings.MEDIA_ROOT + '/owls'
        files = os.listdir(path)
        index = random.randint(0, len(files) - 1)
        return 'owls/' + files[index]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True)
    bio = RichTextField(blank=True, null=True)
    avatar = models.ImageField(default=get_avatar, upload_to='avatars')
    CAT = 'Cats'
    DOG = 'Dogs'
    CHOICES = (
        (CAT, 'Cats'),
        (DOG, 'Dogs')
    )
    cats_or_dogs = models.CharField(max_length=4, choices=CHOICES, default=DOG)
    favourite_colour = models.CharField(max_length=32, blank=True, null=True)
    hobby = models.CharField(max_length=32, blank=True, null=True)
    country = models.ForeignKey(Country, blank=True, null=True)
    city = models.ForeignKey(City, blank=True, null=True)

    def __str__(self):
        return self.user.username

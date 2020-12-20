from django.shortcuts import reverse
from django.db import models
from django.contrib.auth import get_user_model
#from tinymce.models import HTMLField
# from django_quill.fields import QuillField
from froala_editor.fields import FroalaField
from main.models import Profile

class Program(models.Model):
    name = models.CharField(max_length=50)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    #description = models.TextField(max_length=5000, blank=True)
    description = models.TextField(max_length=5000, blank=True) # Using TinyMCE
    #description = QuillField(max_length=5000, blank=True) #using Quill (uninstalled)
    #description = FroalaField() # Froala
    short_description = models.CharField(max_length=60, blank=True)
    link = models.URLField(max_length=200, blank=True)
    image = models.ImageField(upload_to='programs/images/', blank=True)
    members = models.ManyToManyField(Profile, blank=True)

    def __str__(self):
        return self.name + ' (' + str(self.owner) + ')'

    def get_absolute_url(self):
        return reverse('programs:program_detail', kwargs={'pk': self.pk})


class Facilitator(models.Model):
    name = models.CharField(max_length=50)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    description = models.TextField(max_length=5000, blank=True)
    short_description = models.CharField(max_length=60, blank=True)
    link = models.URLField(max_length=200, blank=True)
    image = models.ImageField(upload_to='programs/images/', blank=True)
    programs = models.ManyToManyField(Program, blank=True, related_name='facilitators')
    members = models.ManyToManyField(Profile, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('programs:facilitator_detail', kwargs={'pk': self.pk})


class Facility (models.Model):
    name = models.CharField(max_length=50)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    facilitator = models.ForeignKey(Facilitator, blank=True, on_delete=models.CASCADE)
    description = models.TextField(max_length=250, blank=True)
    link = models.URLField(max_length=200, blank=True)
    image = models.ImageField(upload_to='programs/images/', blank=True)
    location = models.CharField(max_length=50, blank=True)
    members = models.ManyToManyField(Profile, blank=True)

    def __str__(self):
        return self.name

from django.db import models
from django.shortcuts import reverse
from django.contrib.auth import get_user_model
import re
import datetime

class Project(models.Model):
    SCRATCH = 'SC'
    PYTHON = 'PY'
    WEB = 'WE'
    APP = 'AP'
    AI = 'AI'
    MAKE = 'MA'
    TD = '3D'
    VIDEO = 'VI'
    OTHER = 'OT'
    NOTHING = 'NO'
    PROJ_TYPE = [
        (SCRATCH, 'Scratch project'),
        (PYTHON, 'Python project'),
        (WEB, 'Web project'),
        (APP, 'SmartPhone app'),
        (AI, 'AI and Machine learning project'),
        (MAKE, 'Make project'),
        (TD, '#D design project'),
        (VIDEO, 'Video editing project'),
        (OTHER, 'Other kind of project'),
        (NOTHING, 'Not really a project'),
    ]

    OPEN = 'OPN'
    APPROVED = 'APP'
    REVIEWED = 'REV'
    DONE = 'DON'
    PROJ_STATE = [
        (OPEN, 'Opened new project'),
        (APPROVED, 'Project is approved'),
        (REVIEWED, 'Project has been reviewed'),
        (DONE, 'Project is done'),
    ]

    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    project_type = models.CharField(max_length=2, choices=PROJ_TYPE, default=NOTHING)
    project_state = models.CharField(max_length=3, choices=PROJ_STATE, default=OPEN)
    short_description = models.CharField(max_length=140)
    description = models.TextField(max_length=5000, blank=True, null=True)
    youtube = models.CharField(max_length=200, blank=True, null=True)
    embed_link = models.CharField(max_length=300, blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('projects:project_detail', kwargs={'pk': self.pk})


class Pic(models.Model):
    title = models.CharField(max_length=140, blank=True, null=True)
    image = models.ImageField(upload_to='projects/images/')
    project = models.ForeignKey(Project, related_name='images', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'Image_{self.pk} - project {self.project}'


class Link(models.Model):
    title = models.CharField(max_length=140, blank=True, null=True)
    project = models.ForeignKey(Project, related_name='links', on_delete=models.CASCADE, null=True)
    link = models.URLField()

    def __str__(self):
        return f'link_{self.pk} - project {self.project}'

class Track(models.Model):
    pass


class Schadule(models.Model):
    pass

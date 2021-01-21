from django.db import models
from django.shortcuts import reverse
from django.contrib.auth import get_user_model
import re
import datetime
from django.utils import timezone


class Camp(models.Model):
    title = models.CharField(max_length=255, unique=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    departement = models.CharField(max_length=50, blank=True)
    participating_num = models.IntegerField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('funnel:camp_detail', kwargs={'pk': self.pk})

class MasterStage(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=1000, blank=True)

    def __str__(self):
        return f'Master Stage: {self.title}'


class Stage(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=1000, blank=True)
    reference = models.ForeignKey(MasterStage, models.SET_NULL, blank=True, null=True)
    camp = models.ForeignKey(Camp, related_name='stages', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    start_ww = models.IntegerField(blank=True, null=True) # i.e. 2133
    end_ww = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f'{self.camp.title} - {self.title}'


class MasterTask(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=5000, blank=True)
    master_stage = models.ForeignKey(MasterStage, related_name='master_tasks', on_delete=models.CASCADE)

    def __str__(self):
        return f'Master Task: {self.title}'


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=5000, blank=True)
    reference = models.ForeignKey(MasterTask, models.SET_NULL, blank=True, null=True)
    stage = models.ForeignKey(Stage, related_name='tasks', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.stage.camp.title} - {self.stage.title} - {self.title}'


class MasterItem(models.Model):
    title = models.CharField(max_length=255)
    master_task = models.ForeignKey(MasterTask, related_name='master_items', on_delete=models.CASCADE)

    def __str__(self):
        return f'Master Item: {self.title}'


class Item(models.Model):
    title = models.CharField(max_length=255)
    reference = models.ForeignKey(MasterItem, models.SET_NULL, blank=True, null=True)
    task = models.ForeignKey(Task, related_name='items', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    complete_data = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.task.stage.camp.title} - {self.task.stage.title} - {self.task.title} - {self.title}'

    def complete(self):
        self.complete_data = timezone.now()

    def decomplete(self):
        self.complete_data = None

class MasterCollateral(models.Model):
    FILE = 'FI'
    LINK = 'LI'
    IMAGE = 'IM'
    COLL_TYPE = [
        (FILE, 'File'),
        (LINK, 'Link'),
        (IMAGE, 'Image'),
    ]


    description = models.CharField(max_length=255, blank=True)
    master_item = models.ForeignKey(MasterItem, related_name='master_collaterals', on_delete=models.CASCADE)
    collateral_type = models.CharField(max_length=2, choices=COLL_TYPE)
    url = models.URLField(blank=True)
    file = models.FileField(upload_to='funnel/files/', blank=True)
    image = models.ImageField(upload_to='funnel/images/', blank=True)

class Collateral(models.Model):
    FILE = 'FI'
    LINK = 'LI'
    IMAGE = 'IM'
    COLL_TYPE = [
        (FILE, 'File'),
        (LINK, 'Link'),
        (IMAGE, 'Image'),
    ]

    description = models.CharField(max_length=255, blank=True)
    item = models.ForeignKey(Item, related_name='collaterals', on_delete=models.CASCADE)
    reference = models.ForeignKey(MasterCollateral, models.SET_NULL, blank=True, null=True)
    collateral_type = models.CharField(max_length=2, choices=COLL_TYPE)
    url = models.URLField(blank=True)
    file = models.FileField(upload_to='funnel/files/', blank=True)
    image = models.ImageField(upload_to='funnel/images/', blank=True)

    def __str__(self):
        return self.description + ' - ' + self.collateral_type

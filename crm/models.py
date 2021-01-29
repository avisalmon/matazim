from django.db import models
from django.shortcuts import reverse
from django.contrib.auth import get_user_model
import re
import datetime


class Contact(models.Model):
    ''' Contact person class '''
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=5000, blank=True)
    email = models.EmailField(max_length=255, blank=True)
    link = models.URLField(max_length=255, blank=True)
    strategic_comment = models.CharField(max_length=255, blank=True)
    next_step = models.TextField(max_length=5000, blank=True)
    tizkoret = models.DateTimeField(blank=True, null=True)
    phone = models.CharField(max_length=16, blank=True)

    class Meta:
        ordering = ['-tizkoret', 'strategic_comment']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('crm:contact_detail', kwargs={'pk': self.pk})


class Note(models.Model):
    writer = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    comment = models.TextField(max_length=5000)
    contact = models.ForeignKey(Contact, related_name='comments', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'Comment for {self.contact.name} by {self.writer.username} - Date: {self.created}'

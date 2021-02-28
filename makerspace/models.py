from django.db import models
from django.shortcuts import reverse
from django.contrib.auth import get_user_model
import datetime


class Part(models.Model):
    INTELHA = 'IH'
    INTELPE = 'IP'
    INTELJE = 'IJ'
    AVI = 'AS'
    GIL = 'GT'
    SPACE = [
        (INTELHA, 'Intel Haifa makerspce'),
        (INTELPE, 'Intel Petach Tikva maker space'),
        (INTELJE, 'Intel Jerusalem maker space'),
        (AVI, 'Avi Salmon maker space'),
        (GIL, 'Gil Tal maker space'),
    ]

    GIVE = 'GI'
    SELL = 'SE'
    LOAN = 'LO'
    MODE = [
        (GIVE, 'Willing to give away for a good reason'),
        (SELL, 'Willing to sell'),
        (LOAN, 'Willing to loan for a good reason'),
    ]

    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='makerspace/images/', blank=True)
    link = models.URLField(blank=True)
    location = models.CharField(max_length=2, choices=SPACE)
    sub_location = models.CharField(max_length=20, blank=True)
    mode = models.CharField(max_length=2, choices=MODE)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    contact = models.CharField(max_length=50, blank=True, default='avi.salmon@intel.com')
    many = models.BooleanField(default=False)
    critical = models.BooleanField(default=False)

    class Meta:
        ordering = ['-critical', 'location']
    def __str__(self):
        return f'{self.title} - {self.location}'

    def get_absolute_url(self):
        return reverse('makerspace:part_detail', kwargs={'pk': self.pk})


class Item(models.Model):
    part = models.ForeignKey(Part, related_name='items', on_delete=models.CASCADE)
    location = models.CharField(max_length=100, default='')
    return_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f'{self.part.title} - {self.id}'

    def get_absolute_url(self):
        return reverse('makerspace:part_detail', kwargs={'pk': self.part.pk})

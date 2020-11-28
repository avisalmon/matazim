from django.db import models
from django.shortcuts import reverse
from django.contrib.auth import get_user_model
from tinymce.models import HTMLField
import re
import datetime


class Hack(models.Model):
    title = models.CharField(max_length=50)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    short_description = models.TextField(max_length=150, blank=True)
    description = HTMLField(max_length=5000, blank=True)
    image = models.ImageField(upload_to='hack/images/', blank=True)
    youtube = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # parsing youtube id out of url string:
        regex = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})')
        match = regex.match(self.youtube)
        if match:
            self.youtube = match.group('id')
        super(Hack, self).save(*args, **kwargs)

    # def get_absolute_url(self):
    #     return reverse('hack:hack_detail', kwargs={'pk': self.pk})


class Team(models.Model):
    hack = models.ForeignKey(Hack, on_delete=models.CASCADE, related_name='teams')
    title = models.CharField(max_length=50)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    description = HTMLField(max_length=5000, blank=True)
    image = models.ImageField(upload_to='hack/images/', blank=True)
    youtube = models.CharField(max_length=200, blank=True)
    result = models.URLField(max_length=250, blank=True)

    def __str__(self):
        return str(self.title) + '(' + str(self.hack) + ')'

    def save(self, *args, **kwargs):
        # parsing youtube id out of url string:
        regex = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})')
        match = regex.match(self.youtube)
        if match:
            self.youtube = match.group('id')
        super(Team, self).save(*args, **kwargs)

    # def get_absolute_url(self):
    #     return reverse('hack:team_detail', kwargs={'pk': self.pk})


class Schedule(models.Model):
    hack = models.ForeignKey(Hack, on_delete=models.CASCADE, related_name='schedules')
    title = models.CharField(max_length=150)
    time = models.DateTimeField(blank=True)
    meeting_link = models.URLField(max_length=250, blank=True)

    def __str__(self):
        return f'{self.title} ({self.hack})'


class Rating(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    stars = models.IntegerField(default=0)

    class Meta:
        unique_together = [['user', 'team']]

    def __str__(self):
        return f'{self.user} rated {self.team}: {self.stars}'


class Comment(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    comment = models.TextField(max_length=150)

    def __str__(self):
        return f'{self.user} --> {self.team}:'

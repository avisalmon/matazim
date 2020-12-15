from django.db import models
from django.shortcuts import reverse
from django.contrib.auth import get_user_model
from tinymce.models import HTMLField
import re
import datetime


class Course(models.Model):
    title = models.CharField(max_length=50)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    short_description = models.TextField(max_length=150, blank=True)
    hebrew = models.BooleanField(default=True)
    description = HTMLField(max_length=5000, blank=True)
    image = models.ImageField(upload_to='learn/images/', blank=True)
    predecessor = models.ManyToManyField("self", blank=True, symmetrical=False)
    youtube = models.CharField(max_length=200, blank=True)
    members = models.ManyToManyField(get_user_model(), through='Registration', related_name='members')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # parsing youtube id out of url string:
        regex = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})')
        match = regex.match(self.youtube)
        if  match:
            self.youtube = match.group('id')
        super(Course, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('learn:course_detail', kwargs={'pk': self.pk})


class Lesson(models.Model):
    SCRATCH = 'SC'
    PYTHON = 'PY'
    YOUTUBE = 'YO'
    LINK = 'LI'
    TEXT = 'TX'
    FUSION = 'FU'
    TINKERCAD = 'TI'
    NOTHING = 'NO'
    TASK_TYPE = [
        (SCRATCH, 'Scratch project link'),
        (PYTHON, 'Python Kaggle link'),
        (YOUTUBE, 'YouTube link'),
        (LINK, 'general link'),
        (TEXT, 'Text answer'),
        (FUSION, 'Fusion 360 link'),
        (TINKERCAD, 'TinkerCad link'),
        (NOTHING, 'No task requiered'),
    ]

    title = models.CharField(max_length=100)
    description = HTMLField(max_length=5000, blank=True)
    pre_lesson = models.OneToOneField('self',
                                      blank=True,
                                      related_name='next_lesson',
                                      null=True,
                                      on_delete=models.SET_NULL)
    youtube = models.CharField(max_length=200, blank=True)
    challenge_type = models.CharField(max_length=2, choices=TASK_TYPE, default=NOTHING)
    challenge = HTMLField(max_length=5000, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    members = models.ManyToManyField(get_user_model(), through='Completion')

    class Meta:
        ordering = ['title']

    def __str__(self):
        return str(self.course) + ' --> ' + str(self.title)

    def save(self, *args, **kwargs):
        # parsing youtube id out of url string:
        regex = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})')
        match = regex.match(self.youtube)
        if  match:
            self.youtube = match.group('id')
        super(Lesson, self).save(*args, **kwargs)

    @property
    def display_title(self):
        ''' cleaning the title for display '''
        display_title = self.title
        regex = re.compile(r'\s*\d*\s*(.*)')
        match = regex.match(self.title)
        if match:
            display_title = match.group(1)

        return display_title

class Completion(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True)
    completed = models.DateField(null=True, blank=True)
    challenge_answer = models.CharField(max_length=200, blank=True)
    challenge_link = models.CharField(max_length=300, blank=True)
    notes = HTMLField(max_length=10000, blank=True)
    pre_completion = models.OneToOneField('self',
                                          blank=True,
                                          related_name='next_completion',
                                          null=True,
                                          on_delete=models.SET_NULL)

    class Meta:
        unique_together = [['user', 'lesson']]
        ordering = ['lesson']

    def __str__(self):
        return f'Completion for {self.user}, Course: {self.lesson.course}, Lesson: {self.lesson}'


    @property
    def test_completion(self):
        ''' Test that challenge succesfuly posted'''
        # TBD code that tests passing this lesson.
        if self.lesson.challenge_type != Lesson.NOTHING:
            if not self.challenge_link:
                return False

        return True

    def get_absolute_url(self):
        return reverse('learn:completion_detail', kwargs={'pk': self.pk})


class Registration(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='registrations')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    last_completion = models.ForeignKey(Completion, on_delete=models.CASCADE, blank=True, null=True, default=None)
    start_date = models.DateField(auto_now_add=True)
    complete_date = models.DateField(blank=True, null=True)
    stars = models.IntegerField(default=0)
    comments = HTMLField(blank=True)

    class Meta:
        unique_together = [['user', 'course']]

    def __str__(self):
        return f'{self.course} (for user: {self.user})'

    @property
    def need_to_message_about_completion(self):
        ''' will return True only once when graduating'''
        completions = Completion.objects.filter(user=self.user,
                                                lesson__course=self.course)
        done = True
        for completion in completions:
            if not completion.completed:
                done = False

        if done:
            if (self.complete_date==None or self.complete_date==''):
                self.complete_date = datetime.datetime.now()
                self.save()
                return True
            elif self.stars == 0:
                return True
            else:
                return False

    @property
    def precentage(self):
        '''returns precentage of completion of this registration'''
        completions = Completion.objects.filter(user=self.user,
                                                lesson__course=self.course)
        total = 0
        completed = 0

        for completion in completions:
            total += 1
            if completion.completed:
                completed += 1

        if total > 0:
            return int(completed/total*100)
        else:
            return 0

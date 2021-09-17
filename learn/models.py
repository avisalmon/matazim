from django.db import models
from django.shortcuts import reverse
from django.contrib.auth import get_user_model
from programs.models import Program
#from tinymce.models import HTMLField
import re
import datetime
import uuid
import os


class Course(models.Model):
    title = models.CharField(max_length=50)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    short_description = models.TextField(max_length=150, blank=True)
    hebrew = models.BooleanField(default=True)
    description = models.TextField(max_length=5000, blank=True)
    image = models.ImageField(upload_to='learn/images/', blank=True)
    predecessor = models.ManyToManyField("self", blank=True, symmetrical=False)
    youtube = models.CharField(max_length=200, blank=True)
    members = models.ManyToManyField(get_user_model(), through='Registration', related_name='members')
    published = models.BooleanField(default=False)

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
    IMAGE = 'IM'
    NOTHING = 'NO'
    TASK_TYPE = [
        (SCRATCH, 'Scratch project link'),
        (PYTHON, 'Python Kaggle link'),
        (YOUTUBE, 'YouTube link'),
        (LINK, 'general link'),
        (TEXT, 'Text answer'),
        (FUSION, 'Fusion 360 link'),
        (TINKERCAD, 'TinkerCad link'),
        (IMAGE, 'image'),
        (NOTHING, 'No task requiered'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField(max_length=5000, blank=True)
    pre_lesson = models.OneToOneField('self',
                                      blank=True,
                                      related_name='next_lesson',
                                      null=True,
                                      on_delete=models.SET_NULL)
    youtube = models.CharField(max_length=200, blank=True)
    challenge_type = models.CharField(max_length=2, choices=TASK_TYPE, default=NOTHING)
    challenge = models.TextField(max_length=5000, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    members = models.ManyToManyField(get_user_model(), through='Completion')
    note = models.TextField(default='Notes for this lesson:\n\nYou can write your own notes here...')

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

    def get_absolute_url(self):
        return reverse('learn:course_update', kwargs={'pk': self.course.pk})

    @property
    def display_title(self):
        ''' cleaning the title for display '''
        display_title = self.title
        #regex = re.compile(r'\s*\d*\s*(.*)')
        regex = re.compile(r'[\s\d\-\.]*(.*)')
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
    notes = models.TextField(max_length=10000, blank=True)
    pre_completion = models.OneToOneField('self',
                                          blank=True,
                                          related_name='next_completion',
                                          null=True,
                                          on_delete=models.SET_NULL)
    note = models.TextField(default='Notes for this lesson:')
    image = models.ImageField(upload_to='learn/images/', blank=True, null=True)

    class Meta:
        unique_together = [['user', 'lesson']]
        ordering = ['lesson']

    def __str__(self):
        return f'Completion for {self.user}, Course: {self.lesson.course}, Lesson: {self.lesson}'


    @property
    def test_completion(self):
        ''' Test that challenge succesfuly posted'''
        # TBD code that tests passing this lesson.
        if self.lesson.challenge_type == Lesson.IMAGE:
            if not self.image:
                return False
            else:
                return True

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
    comments = models.TextField(blank=True)

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

    @property
    def more_lessons(self):
        num_completions = Completion.objects.filter(user=self.user,
                                                   lesson__course=self.course).count()
        num_lessons = Lesson.objects.filter(course=self.course).count()
        if num_lessons > num_completions:
            return True
        else:
            return False


class Batch(models.Model):
    ''' bulk order of several items '''
    title = models.CharField(max_length=50)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    owner_mail = models.EmailField(max_length=250, blank=True)
    description = models.TextField(max_length=150, blank=True)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    amount = models.IntegerField(default=1)
    amount_left = models.IntegerField(default=999)
    suppliers = models.ManyToManyField(get_user_model(), related_name='batches')
    program = models.ForeignKey(Program, null=True, blank=True, on_delete=models.SET_NULL)
    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.SET_NULL)
    completed = models.BooleanField(default=False)
    done = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('learn:batch_detail', kwargs={'pk': self.pk})

    # @property
    # def aligable(self):
    #     return True

    def update_batch(self):
        print(f' updating batch {self}')
        orders = Order.objects.filter(batch=self)
        print(f'orders are {orders}')
        print(f'len of orders {len(orders)}')
        print(f'amount={self.amount}')
        self.amount_left = self.amount - len(orders)
        print(f'amount left = {self.amount_left}')
        if self.amount_left <= 0:
            self.completed = True
        else:
            self.completed = False
        if self.completed:
            #check for Does
            self.done = True
            for order in orders:
                if not (order.printed and order.sent):
                    self.done = False
                    break

        print(f'complitted flag = {self.completed}')

class Order(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    batch = models.ForeignKey(Batch, null=True, on_delete=models.SET_NULL, related_name='orders')
    order_date = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=500, verbose_name=u"כתובת למשלוח", blank=False)
    email = models.EmailField(max_length=250, verbose_name=u"דואר אלקטרוני", blank=False)
    phone = models.CharField(max_length=15, verbose_name=u"טלפון", blank=False)
    file = models.FileField(upload_to='learn/files/', verbose_name=u"צרף קובץ", blank=True, null=True)
    printed = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)
    sent_date = models.DateField(null=True, blank=True, default=None)
    supplier_comment = models.CharField(max_length=150, blank=True, null=True)
    error = models.CharField(max_length=250, default='')

    def __str__(self):
        return f'Order for: {self.user} - course: {self.course}'

    def get_absolute_url(self):
        return reverse('learn:order_detail', kwargs={'pk': self.pk})

    def check_if_approved(self):
        self.error= ''
        print(f'checking approval for order {self}')
        try:
            registration = Registration.objects.get(user=self.user, course=self.course)
        except:
            self.error = f'You did not register yet to the training - { self.course }'
            if self.batch:
                self.batch = None
            return False
        if not registration.complete_date:
            self.error = f'You have to complete the course { self.batch.course } - you did so far { registration.precentage }% of it'
            if self.batch:
                self.batch = None
            return False
        if not self.file:
            self.error = f'You need to upload a file for printing. stl format'
            if self.batch:
                self.batch = None
            return False

        filename = str(self.file)
        if not '.stl' in filename:
            self.error = 'The file you attache must be an .stl file'
            if self.batch:
                self.batch = None
            return False

        if not (self.address and self.email and self.phone and self.file):
            print(1)
            self.error = 'You can get your print but you need to fill all details (address, phone, email and a file)'
            if self.batch:
                self.batch = None
            return False
        return True

    @property
    def filename(self):
        return os.path.basename(self.file.name)

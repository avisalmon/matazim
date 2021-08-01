from django.db import models
#from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
#from tinymce.models import HTMLField
from django.shortcuts import reverse


BIO_MAX_LENGTH = 12800
DESCRIPTION_MAX_LENGTH = 120
LONG_DESCRIPTION_MAX_LENGTH = 1024

PHONE_NUMBER_LENGTH = 15
MAX_EMAIL_LENGTH = 50
MAX_USERNAME_LENGTH = 40
MAX_URL_LENGTH = 256

FIELD_MAX_LENGTH = 50
FIELD_MAX_DIGITS = 10
FIELD_DECIMAL_PLACES = 8

class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    bio = models.TextField(max_length=5000, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True, help_text="Please use the following format: <em>YYYY-MM-DD</em>.")
    image = models.ImageField(upload_to='main/images/', blank=True, null=True)
    perach = models.BooleanField(default=False)
    level = models.IntegerField(default=0)
    mataz = models.BooleanField(default=False)
    mentor = models.BooleanField(default=False)
    fake = models.BooleanField(default=False)
    top_goal = models.TextField(max_length=5000, blank=True)
    program_conn = models.ForeignKey("programs.Program", blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f'Profile for {self.user}'

@receiver(post_save, sender=get_user_model())
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=get_user_model())
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Status(models.Model):
    ''' User status '''
    user = models.ForeignKey(get_user_model(),
                             blank=True,
                             on_delete=models.CASCADE,
                             related_name='statuses')
    written_by = models.ForeignKey(get_user_model(),
                             blank=True, null=True,
                             on_delete=models.CASCADE)
    text = models.TextField(max_length=LONG_DESCRIPTION_MAX_LENGTH,
                                null=True)
    image = models.ImageField(upload_to='main/images/', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'status for {str(self.user.username)} ; created {str(self.created)}'

    class Meta:
        ordering = ['-created']


class UserLink(models.Model):
    """A User contact info model"""
    provider = models.CharField(max_length=FIELD_MAX_LENGTH)
    display_name = models.TextField(max_length=MAX_USERNAME_LENGTH,
                                    null=True,
                                    blank=True)
    username = models.TextField(max_length=MAX_USERNAME_LENGTH,
                                null=True)
    user = models.ForeignKey(get_user_model(),
                             blank=True,
                             on_delete=models.CASCADE,
                             related_name='links')

    def __str__(self):
        return f'Link-{self.provider} for {self.user} as: ({self.username})'


# TODO: Might want to make some changes to the structure of this model.
class UserExperience(models.Model):
    """A User Experience Link model"""
    institution = models.CharField(max_length=FIELD_MAX_LENGTH,)
    experience = models.CharField(max_length=DESCRIPTION_MAX_LENGTH,
                                  blank=True,
                                  default='')
    experience_type = models.CharField(
        max_length=FIELD_MAX_LENGTH, default="work")
    # work, study, prize, project
    start_year = models.IntegerField(blank=True, null=True)
    finish_year = models.IntegerField(blank=True, null=True)
    description = models.CharField(max_length=LONG_DESCRIPTION_MAX_LENGTH,
                                   blank=True,
                                   null=True)
    user = models.ForeignKey(get_user_model(),
                             blank=True,
                             on_delete=models.CASCADE,
                             related_name='experiences')

    def __str__(self):
        return f'Expirience: {self.institution} for {self.user}'


class UserHobby(models.Model):
    """A User Hobby model"""
    title = models.CharField(max_length=FIELD_MAX_LENGTH,)
    description = models.TextField(max_length=LONG_DESCRIPTION_MAX_LENGTH, blank=True)
    icon = models.CharField(max_length=FIELD_MAX_LENGTH, default="dice-d20")
    color = models.CharField(max_length=FIELD_MAX_LENGTH, default="#4169e1")

    user = models.ForeignKey(get_user_model(),
                             #blank=True,
                             on_delete=models.CASCADE,
                             related_name='hobbies')

    def __str__(self):
        return f'Hobby: {self.title} for user: {self.user}'

    def get_absolute_url(self):
        return reverse('main:profile', kwargs={'profile_pk': 0})

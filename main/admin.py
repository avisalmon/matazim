from django.contrib import admin
from .models import Profile, UserLink, UserExperience, UserHobby, Status

admin.site.register(Profile)
admin.site.register(UserLink)
admin.site.register(UserExperience)
admin.site.register(UserHobby)
admin.site.register(Status)

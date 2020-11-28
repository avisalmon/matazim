from django.contrib import admin
from .models import Hack, Team, Schedule, Rating, Comment


# class RegistrationAdmin(admin.ModelAdmin):
#     readonly_fields = ('start_date',)
#
# class CompletionAdmin(admin.ModelAdmin):
#     readonly_fields = ('start_date',)

admin.site.register(Hack)
admin.site.register(Team)
admin.site.register(Schedule)
admin.site.register(Rating)
admin.site.register(Comment)

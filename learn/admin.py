from django.contrib import admin
from .models import Course, Registration, Lesson, Completion


class RegistrationAdmin(admin.ModelAdmin):
    readonly_fields = ('start_date',)
    list_display = ['user', 'course', 'last_completion', 'stars']
    list_filter = ['start_date']
    

class CompletionAdmin(admin.ModelAdmin):
    readonly_fields = ('start_date',)

admin.site.register(Course)
admin.site.register(Registration, RegistrationAdmin)
admin.site.register(Lesson)
admin.site.register(Completion, CompletionAdmin)

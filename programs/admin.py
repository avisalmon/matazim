from django.contrib import admin
from .models import Program, Facilitator, Facility

#admin.site.register(Program)
admin.site.register(Facilitator)
admin.site.register(Facility)

@admin.register(Program)
class QuillPostAdmin(admin.ModelAdmin):
    pass

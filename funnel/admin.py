from django.contrib import admin
from .models import Camp, MasterStage, Stage, MasterTask, \
                    Task, MasterItem, Item, MasterCollateral, \
                    Collateral

admin.site.register(Camp)
admin.site.register(MasterStage)
admin.site.register(Stage)
admin.site.register(MasterTask)
admin.site.register(Task)
admin.site.register(MasterItem)
admin.site.register(Item)
admin.site.register(MasterCollateral)
admin.site.register(Collateral)

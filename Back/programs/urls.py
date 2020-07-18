from django.urls import path
from . import views

app_name='programs'

urlpatterns = [
    path('program/', views.ProgramListView.as_view(),
         name='program_list'),
    path('program/create', views.ProgramCreateView.as_view(),
         name='program_create'),
    path('program/<int:pk>', views.ProgramDetailView.as_view(),
         name='program_detail'),
    path('program/update/<int:pk>', views.ProgramUpdateView.as_view(),
         name='program_update'),
    path('program/delete/<int:pk>', views.ProgramDeleteView.as_view(),
         name='program_delete'),
    path('program/add_member/<int:program_id>/<int:profile_id>',
         views.program_add_member,
         name='program_add_member'),
    path('program/remove_member/<int:program_id>/<int:profile_id>',
         views.program_remove_member,
         name='program_remove_member'),
]

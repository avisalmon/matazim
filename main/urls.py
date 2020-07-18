from django.urls import path
from . import views

app_name='main'

urlpatterns = [
    path('profile/', views.my_profile_view, name='my_profile_view'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('profile/<int:profile_pk>',
         views.profile_view,
         name='profile'),
]

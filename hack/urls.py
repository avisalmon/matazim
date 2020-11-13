from django.urls import path
from . import views

app_name='hack'

urlpatterns = [
    path('home/', views.home, name='home'),
]

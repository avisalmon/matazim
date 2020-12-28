from django.urls import path
from . import views

app_name='projects'

urlpatterns = [
    # *** Projects ***
    path('', views.ProjectListView.as_view(),
         name='project_list'),
    path('<int:pk>', views.ProjectDetailView.as_view(),
         name='project_detail'),
]

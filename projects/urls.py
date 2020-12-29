from django.urls import path
from . import views

app_name='projects'

urlpatterns = [
    # *** Projects ***
    path('', views.ProjectListView.as_view(),
         name='project_list'),
    path('<int:pk>', views.ProjectDetailView.as_view(),
         name='project_detail'),
    path('create/', views.ProjectCreateView.as_view(),
         name='project_create'),
    path('update/<int:pk>', views.ProjectUpdateView.as_view(),
         name='project_update'),
    path('delete/<int:pk>', views.ProjectDeleteView.as_view(),
         name='project_delete'),
    path('add_pic_to_project/<int:project_pk>', views.add_pic,
         name='add_pic'),
    path('add_link_to_project/<int:project_pk>', views.add_link,
         name='add_link'),
    path('image_delete/<int:pk>', views.img_delete,
         name='image_delete'),
    path('link_delete/<int:pk>', views.link_delete,
         name='link_delete'),
]

from django.urls import path
from . import views

app_name='learn'

urlpatterns = [
    path('', views.home,
         name='home'),
    path('course_list/',
         views.CourseListView.as_view(),
         name='course_list'),
    path('course/<int:pk>',
         views.CourseDetailView.as_view(),
         name='course_detail'),
    path('course/sign/<int:pk>',
         views.courseSignView,
         name='course_sign'),
    path('course/unsign/<int:pk>',
         views.course_unsign,
         name='course_unsign'),
    path('completion/<int:pk>',
         views.CompletionDetailView.as_view(),
         name='completion_detail'),
    path('completion/complete/<int:pk>',
         views.completion_done,
         name='completion_done'),
    # path('course/complete_message/<int:registration_pk>',
    #      views.course_complete_message,
    #      name='course_complete_message'),
]
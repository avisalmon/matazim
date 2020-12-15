from django.urls import path
from . import views

app_name='learn'

urlpatterns = [
    path('', views.home,
         name='home'),
         # *** Course ******
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
    path('course/rate/<int:pk>/<int:rate>', views.courseRate, name='course_rate'),
    # ****** Completion ********
    path('completion/<int:pk>',
         views.CompletionDetailView.as_view(),
         name='completion_detail'),
    path('completion/complete/<int:pk>',
         views.completion_done,
         name='completion_done'),
    path('completion/scratch_task/<int:completion_pk>',
         views.scratch_post,
         name='scratch_post'),
    path('completion/fusion_task/<int:completion_pk>',
      views.fusion_post,
      name='fusion_post'),
    path('completion/tinkercad_task/<int:completion_pk>',
      views.tinkercad_post,
      name='tinkercad_post'),
    # path('course/complete_message/<int:registration_pk>',
    #      views.course_complete_message,
    #      name='course_complete_message'),

    # *********** Reports *************
    path('report/', views.learnReport, name='learn_report'),
    path('report/<int:pk>', views.personal_report, name='personal_report'),
]

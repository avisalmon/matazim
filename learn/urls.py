from django.urls import path, include
from . import views
from rest_framework import routers

app_name='learn'

router = routers.DefaultRouter()
router.register('course', views.CourseViewSet)

urlpatterns = [
    path('', views.home,
         name='home'),
         # *** Course ******
    path('course_list/',
         views.CourseListView.as_view(),
         name='course_list'),
    path('course/create/',
         views.CourseCreateView.as_view(),
         name='course_create'),
    path('course/admin/<int:pk>',
         views.CourseUpdateView.as_view(),
         name='course_update'),
    path('course/<int:pk>',
         views.CourseDetailView.as_view(),
         name='course_detail'),
    path('course/sign/<int:pk>',
         views.courseSignView,
         name='course_sign'),
    path('course/confirm_unsign/<int:pk>',
         views.course_confirm_unsign,
         name='course_confirm_unsign'),
    path('course/unsign/<int:pk>',
         views.course_unsign,
         name='course_unsign'),
    path('course/rate/<int:pk>/<int:rate>', views.courseRate, name='course_rate'),

    # ****** Lesson ************
    path('lesson/create/<int:course_pk>',
         views.lessonCreateView.as_view(),
         name='lesson_create'),
    # Todo Lesson update
    path('lesson/update/<int:pk>',
         views.LessonUpdateView.as_view(),
         name='lesson_update'),
    # Todo Lesson delete

    # ****** Completion ********
    path('completion/edit_note/<int:pk>',
         views.NoteUpdateView.as_view(),
         name='note_update'),
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
    path('completion/youtube_task/<int:completion_pk>',
      views.youtube_post,
      name='youtube_post'),
    path('completion/immage_task/<int:completion_pk>',
      views.image_post,
      name='image_post'),
    path('update_lessons/<int:registration_pk>',
         views.update_lessons,
         name='update_lessons'),
    # path('course/complete_message/<int:registration_pk>',
    #      views.course_complete_message,
    #      name='course_complete_message'),

    # ***** API ***********************
    path('api/', include(router.urls)),
    # *********** Reports *************
    path('report/', views.learnReport, name='learn_report'),
    path('report/<int:pk>', views.personal_report, name='personal_report'),
    path('report/program/<int:pk>', views.program_report,
         name='program_report'),

    # *** Batch and orders
    path('batch/', views.BatchListView.as_view(),
         name='batch_list'),
    path('batch/<int:pk>', views.BatchDetailView.as_view(),
         name='batch_detail'),
    path('order/create/<int:course_pk>', views.OrderCreateView.as_view(),
         name='order_create'),
    path('order/<int:pk>', views.OrderDetailView.as_view(),
         name='order_detail'),
    path('order/update/<int:pk>', views.OrderUpdateView.as_view(),
         name='order_update'),
    path('order/admin/list/', views.OrderAdminList.as_view(),
         name='order_admin_list'),
    path('order/assign_to_batch/<int:order_pk>', views.assign_to_batch,
         name='assign_to_batch'),
    path('order/remove_batch/<int:order_pk>', views.order_remove_batch,
         name='remove_batch_from_order'),
    path('order/mark_printed/<int:order_pk>', views.order_mark_printed,
         name='order_mark_printed'),
    path('order/mark_unprinted/<int:order_pk>', views.order_mark_unprinted,
         name='order_mark_unprinted'),
    path('order/mark_sent/<int:order_pk>', views.order_mark_sent,
         name='order_mark_sent'),
    path('order/mark_unsent/<int:order_pk>', views.order_mark_unsent,
         name='order_mark_unsent'),
]

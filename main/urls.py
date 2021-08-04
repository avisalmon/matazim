from django.urls import path
from . import views

app_name='main'

urlpatterns = [
        # Profile
    #path('profile/', views.my_profile_view, name='my_profile_view'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('profile/<int:profile_pk>',
         views.profile_view,
         name='profile'),
         # Hobby
    path('profile/add_hobby/', views.add_hobby, name='add_hobby'),
    path('profile/delete_hobby/<int:pk>',
          views.HobbyDeleteView.as_view(),
          name='hobby_delete'),
    path('profile/edit_hobby/<int:pk>',
         views.HobbyUpdateView.as_view(),
         name='hobby_edit'),
    path('profile/add_badge/<int:profile_pk>/<int:badge>',
         views.add_badge,
         name='add_badge'),
    path('profile/add_user_to_program/<int:pk>',
         views.AddUserToProgram.as_view(),
         name='add_user_to_program'),
    # Status
    path('status/create/<int:for_profile_pk>',
         views.StatusCreateForm.as_view(),
         name = 'status_create'),
    path('status/update/<int:pk>',
         views.StatusUpdateView.as_view(),
         name='status_update'),
    path('status/delete/<int:pk>',
         views.StatusDeleteView.as_view(),
         name='status_delete'),
]

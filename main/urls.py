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
]

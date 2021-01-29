from django.urls import path
from . import views

app_name='crm'

urlpatterns = [
    # Contacts
    path('contact_create/', views.ContactCreateForm.as_view(),
         name='contact_create'),
    path('contact_list/', views.ContactListView.as_view(),
         name='contact_list'),
    path('contact_datail/<int:pk>', views.ContactDetailView.as_view(),
         name='contact_detail'),
    path('contact_update/<int:pk>', views.ContactUpdateView.as_view(),
         name='contact_update'),
    path('contact_delete/<int:pk>', views.ContactDeleteView.as_view(),
         name='contact_delete'),
]

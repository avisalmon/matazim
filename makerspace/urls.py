from django.urls import path, include
from . import views

app_name='makerspace'

urlpatterns = [
    path('', views.PartListView.as_view(),
         name='part_list'),
    path('part/<int:pk>', views.PartDetailView.as_view(),
         name='part_detail'),
    path('part/create/', views.PartCreateView.as_view(),
         name='part_create'),
    path('part/update/<int:pk>', views.PartUpdateView.as_view(),
         name='part_update'),
    path('part/delete/<int:pk>', views.PartDeleteView.as_view(),
         name='part_delete'),
    #  **** items *****
    path('item/create/<int:part_pk>/',
         views.create_more_items,
         name='create_more_items'),
    path('item/update/<int:pk>', views.ItemUpdateView.as_view(),
         name='item_update'),
    path('item/delete/<int:pk>', views.ItemDeleteView.as_view(),
         name='item_delete'),
]

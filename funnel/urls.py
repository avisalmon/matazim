from django.urls import path
from . import views

app_name='funnel'

urlpatterns = [
    # Campaign
    path('camp_list/', views.CampListView.as_view(),
         name='camp_list'),
    path('create_camp/', views.CampCreateView.as_view(),
         name='camp_create'),
    path('camp/<int:pk>', views.CampDetailView.as_view(),
         name='camp_detail'),
    path('camp/update/<int:pk>', views.CampUpdateView.as_view(),
         name='camp_update'),
    # Stage CrUD
    path('stage_create/<int:camp_pk>', views.StageCreateView.as_view(),
         name='stage_create'),
    path('stage_update/<int:pk>', views.StageUpdateView.as_view(),
         name='stage_update'),
    path('stage_delete/<int:pk>', views.StageDeleteView.as_view(),
         name='stage_delete'),
    # Task CrUD
    path('task_crate/<int:stage_pk>', views.TaskCreateView.as_view(),
         name='task_create'),
    path('task_update/<int:pk>', views.TaskUpdateView.as_view(),
         name='task_update'),
    path('task_delete/<int:pk>', views.TaskDeleteView.as_view(),
         name='task_delete'),
    # Item CrUD
    path('item_create/<int:task_pk>', views.ItemCreateView.as_view(),
         name='item_create'),
    path('item_detail/<int:pk>', views.ItemDetailView.as_view(),
         name='item_detail'),
    path('item_update/<int:pk>', views.ItemUpdateView.as_view(),
         name='item_update'),
    path('item_delete/<int:pk>', views.ItemDeleteView.as_view(),
         name='item_delete'),
    path('item_complete/<int:pk>', views.item_complete,
         name='item_complete'),
    path('item_decomplete/<int:pk>', views.item_decomplete,
         name='item_decomplete'),
    # Collateral
    # Create:
    path('add_image/<int:item_pk>', views.CollateralAddImage.as_view(),
         name='add_image'),
    path('add_file/<int:item_pk>', views.CollateralAddFile.as_view(),
         name='add_file'),
    path('add_link/<int:item_pk>', views.CollateralAddLink.as_view(),
         name='add_link'),
    # Update:
    path('update_image/<int:pk>', views.CollateralUpdateImage.as_view(),
         name='update_image'),
    path('update_file/<int:pk>', views.CollateralUpdateFile.as_view(),
         name='update_file'),
    path('update_link/<int:pk>', views.CollateralUpdateLink.as_view(),
         name='update_link'),
    # Delete collateral
    path('delete_collateral/<int:pk>', views.CollateralDeleteView.as_view(),
         name='delete_collateral'),
]

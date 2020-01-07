from django.urls import path
from . import views

app_name = 'management'
urlpatterns = [
    path('list/<path:path>', views.show_file_list_page, name='file_list_page'),
    path('share-link/', views.show_share_link_list_page, name='share_link_list_page'),
    path('message/<str:token>/', views.show_message_list_page, name='message_link_list_page'),
    path('trash/', views.show_trash_page, name='trash_list_page'),
    path('share/<str:token>/', views.show_share_download_page, name='share_download_page'),
    path('share/download/<str:token>/', views.api_share_download_file, name='api_share_download_file'),
    path('share/create/<str:real_name>/', views.api_create_share_link, name='api_create_share_link'),
    path('share/delete/<str:token>/', views.api_delete_share_link, name='api_delete_share_link'),

    path('api/file/upload/', views.api_upload_file, name='api_upload_file'),
    path('api/file/download/<str:real_name>/', views.api_download_file, name='api_download_file'),
    path('api/file/delete/<str:real_name>/', views.api_delete_file, name='api_delete_file'),
    path('api/file/rename/<str:real_name>/', views.api_rename_file, name='api_rename_file'),
    path('api/file/recycle/<str:real_name>/', views.api_recycle_file, name='api_recycle_file'),
    path('api/file/recover/<str:real_name>/', views.api_recover_file, name='api_recover_file'),

    path('api/directory/recycle/<str:real_name>/', views.api_recycle_directory, name='api_recycle_directory'),
    path('api/directory/create/', views.api_create_directory, name='api_create_directory'),
    path('api/directory/delete/<str:real_name>/', views.api_delete_directory, name='api_delete_directory'),
    path('api/directory/rename/<str:real_name>/', views.api_rename_directory, name='api_rename_directory'),
    path('api/directory/recover/<str:real_name>/', views.api_recover_directory, name='api_recover_directory'),

    path('api/message/add/<str:token>/', views.api_add_message, name='api_add_message'),
    path('api/space/apply/', views.api_apply_space, name='api_apply_space'),

    path('api/set/move/', views.api_set_move, name='api_set_move'),
    path('api/set/copy/', views.api_set_copy, name='api_set_copy'),
    path('api/do/move/', views.api_do_move, name='api_do_move'),
    path('api/do/copy/', views.api_do_copy, name='api_do_copy'),
]

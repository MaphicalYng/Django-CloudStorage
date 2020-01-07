from django.urls import path
from . import views

app_name = "admins"
urlpatterns = [
    #href
    path('index/', views.show_index_page_admins, name='show_index_page_admins'),
    path('sign-in/', views.show_sign_in_page_admins, name='show_sign_in_page_admins'),
    path('sign-up/', views.show_sign_up_page_admins, name='show_sign_up_page_admins'),
    path('reset-password/', views.show_reset_password_page_admins, name='show_reset_password_page_admins'),
    path('users/', views.show_users_page_admins, name='show_users_page_admins'),
    path('user/<int:user_id>/', views.show_user_page_admins, name='show_user_page_admins'),
    path('check/', views.show_check_page_admins, name='show_check_page_admins'),
    path('file/<int:file_id>/', views.show_file_page_admins, name='show_file_page_admins'),
    path('files/', views.show_files_page_admins, name='show_files_page_admins'),
    path('change_type/', views.show_change_type_page_admins, name='show_change_type_page_admins'),
    path('backup/', views.show_backup_page_admins, name='show_change_backup_admins'),
    path('encrypt/', views.show_encrypt_page_admins, name='show_change_encrypt_admins'),
    path('space-check/', views.show_space_check_page_admins, name='show_space_check_page_admins'),
    # path('<slug:redirect>', views.web_page_redirect, name='web_page_redirect'),

    #api
    path('api-sign-in-admin/', views.api_login_admins, name='api_login_admins'),
    path('api-add-user-admin/', views.api_add_user, name='api_add_user'),
    path('api-del-user-admin/', views.api_del_user, name='api_del_user'),
    path('api-upd-user-admin/', views.api_upd_user, name='api_upd_user'),
    path('api-check-user-admin/', views.api_check_user, name='api_check_user'),
    path('api-del-file-admin/', views.api_del_file, name='api_del_file'),
    path('api-upd-file-admin/', views.api_upd_file, name='api_upd_file'),
    path('api-add-file-type-admin/', views.api_add_file_type, name='api_add_fle_type'),
    path('api-del-file-type-admin/', views.api_del_file_type, name='api_del_fle_type'),
    path('api-back-up-admin/', views.api_back_up, name='api_back_up'),
    path('api-reset-psw-admin/', views.api_reset_psw, name='api_reset_psw'),
    path('api-space-check-admin/', views.api_space_check, name='api_space_check'),

]
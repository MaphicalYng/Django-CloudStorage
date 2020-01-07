from django.urls import path
from . import views

app_name = "user"
urlpatterns = [
    path('login/', views.show_login_page, name='login_page'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/logout/', views.api_logout, name='api_logout'),
    path('api/register/', views.api_register, name='api_register')
]
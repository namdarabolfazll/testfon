from django.urls import path
from .views import UserLoginView, register, logout_view

app_name = 'authentication'

urlpatterns = [
    path(
        'login/',
        UserLoginView.as_view(),
        name='login'
    ),

    path(
        'register/',
        register,
        name='register'
    ),

    path(
        'logout/',
        logout_view,
        name='logout'
    ),
]
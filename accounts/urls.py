from django.urls import path
from . import views

urlpatterns = [
    path('me', views.me, name='auth_me'),
    path('signup', views.signup_view, name='auth_signup'),
    path('login', views.login_view, name='auth_login'),
    path('logout', views.logout_view, name='auth_logout'),
]

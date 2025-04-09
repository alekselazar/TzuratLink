from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='reader'),
    path('dafyomi/', views.daf_yomi, name='daf yomi'),
    path('dafyomi/<str:amud>', views.daf_yomi, name='daf yomi')
]
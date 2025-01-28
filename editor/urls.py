from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='editor'),
    path('reviewpage/', views.review_page, name='review page'),
    path('completepage/', views.complete_page, name='complete page'),
    path('savesentance/', views.save_sentance, name='save sentance'),
    path('translates/', views.translates, name='save translate')
]
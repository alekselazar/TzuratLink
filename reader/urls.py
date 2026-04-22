from django.urls import path, re_path

from . import views

urlpatterns = [
    path('health/', views.health, name='health'),
    path('', views.index, name='reader'),
    path('dafyomi/', views.daf_yomi, name='daf yomi'),
    path('dafyomi/<str:amud>', views.daf_yomi, name='daf yomi'),
    path('api/page/<path:ref>', views.get_page_data, name='get_page_data'),
    # Catch-all route for client-side routing (must be last)
    # Captures any remaining path for React Router to handle
    re_path(r'^(?P<path>.*)$', views.reader_catchall, name='reader_catchall'),
]
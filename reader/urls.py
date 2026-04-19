from django.urls import path, re_path

from . import views

urlpatterns = [
    path('health/', views.health, name='health'),
    path('', views.index, name='reader'),
    path('dafyomi/', views.dafyomi_redirect, name='dafyomi_redirect'),
    path('page/<path:ref>', views.page_view, name='page_view'),
    path('api/page/<path:ref>', views.get_page_data, name='get_page_data'),
    path('api/dafyomi/next/<path:ref>', views.get_next_page, name='get_next_page'),
    path('api/dafyomi/prev/<path:ref>', views.get_prev_page, name='get_prev_page'),
    # Catch-all route for client-side routing (must be last)
    re_path(r'^(?P<path>.*)$', views.reader_catchall, name='reader_catchall'),
]
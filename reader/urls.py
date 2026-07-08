from django.urls import path, re_path

from . import views

urlpatterns = [
    path('health/', views.health, name='health'),
    path('health', views.health, name='health_noslash'),
    path('', views.homepage, name='homepage'),
    path('dafyomi/', views.dafyomi_redirect, name='dafyomi_redirect'),
    path('page/<path:ref>', views.page_view, name='page_view'),
    path('tractate/<str:name>', views.tractate_view, name='tractate_view'),
    path('api/tractate/<str:name>', views.tractate_api, name='tractate_api'),
    path('api/page/<path:ref>', views.get_page_data, name='get_page_data'),
    path('api/render/<path:ref>', views.render_page, name='render_page'),
    path('api/library', views.library_api, name='library_api'),
    path('api/next/<path:ref>', views.get_next_page, name='get_next_page'),
    path('api/prev/<path:ref>', views.get_prev_page, name='get_prev_page'),
    path('api/debug/<path:ref>', views.debug_page, name='debug_page'),
    re_path(r'^(?P<path>.*)$', views.reader_catchall, name='reader_catchall'),
]

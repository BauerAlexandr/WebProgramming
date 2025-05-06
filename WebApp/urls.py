from django.urls import path
from . import views, converters
from django.conf import settings
from django.conf.urls.static import static
from django.urls import register_converter

register_converter(converters.DateConverter, "yyyy")

urlpatterns = [
    path('', views.index, name='home'),
    path('category/<int:cat_id>/', views.show_category, name='category'),
    
    # Маршруты для работы с часами
    path('watches/', views.watch_list, name='watch_list'),
    path('watches/<slug:slug>/', views.watch_detail, name='watch'),
    
    # Маршруты для работы с категориями
    path('categories/', views.category_list, name='category_list'),
    
    # Служебные маршруты
    path('fix-slugs/', views.fix_missing_slugs, name='fix_missing_slugs'),
    path('tag/<slug:tag_slug>/', views.show_tag, name='tag'),
    path('stats/', views.stats, name='stats'),

    path('add-watch/', views.add_watch, name='add_watch'),
    path('upload-file/', views.upload_file, name='upload_file'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
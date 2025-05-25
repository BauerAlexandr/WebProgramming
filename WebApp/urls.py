from django.urls import path
from . import views, converters
from django.conf import settings
from django.conf.urls.static import static
from django.urls import register_converter

register_converter(converters.DateConverter, "yyyy")

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('category/<int:cat_id>/', views.CategoryView.as_view(), name='category'),
    
    # Маршруты для работы с часами
    path('watches/', views.WatchListView.as_view(), name='watch_list'),
    path('watches/<slug:slug>/', views.WatchDetailView.as_view(), name='watch'),
    
    # Маршруты для работы с категориями
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    
    # Служебные маршруты
    path('fix-slugs/', views.FixMissingSlugsView.as_view(), name='fix_missing_slugs'),
    path('tag/<slug:tag_slug>/', views.TagView.as_view(), name='tag'),
    path('stats/', views.StatsView.as_view(), name='stats'),

    path('add-watch/', views.AddWatchView.as_view(), name='add_watch'),
    path('edit/<slug:slug>/', views.UpdateWatchView.as_view(), name='edit_watch'),
    path('delete/<slug:slug>/', views.DeleteWatchView.as_view(), name='delete_watch'),
    path('upload-file/', views.UploadFileView.as_view(), name='upload_file'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
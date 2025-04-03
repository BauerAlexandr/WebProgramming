from django.urls import path
from . import views, converters
from django.urls import register_converter

register_converter(converters.DateConverter, "yyyy")

urlpatterns = [
    path('', views.index, name='home'),
    path('client/<int:client_id>/', views.client, name='client'),
    path('category/<int:cat_id>/', views.show_category, name='category'),
    path('watch/<int:watch_id>/', views.show_watch, name='watch'),
    
    # Маршруты для работы с часами
    path('watches/', views.watch_list, name='watch_list'),
    path('watches/create/', views.watch_create, name='watch_create'),
    path('watches/<slug:slug>/', views.watch_detail, name='watch_detail'),
    path('watches/<slug:slug>/update/', views.watch_update, name='watch_update'),
    path('watches/<slug:slug>/delete/', views.watch_delete, name='watch_delete'),
    
    # Маршруты для работы с категориями
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<slug:slug>/update/', views.category_update, name='category_update'),
    path('categories/<slug:slug>/delete/', views.category_delete, name='category_delete'),
    
    # Служебные маршруты
    path('fix-slugs/', views.fix_missing_slugs, name='fix_missing_slugs'),
]

from django.urls import path
from . import views, converters
from django.urls import register_converter

register_converter(converters.DateConverter, "yyyy")

urlpatterns = [
    path('', views.index, name='home'),
    path('client/<int:client_id>/', views.client, name='client'),
    path('category/<int:cat_id>/', views.show_category, name='category'),
    path('watch/<int:watch_id>/', views.show_watch, name='watch'),
]

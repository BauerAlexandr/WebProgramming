from django.contrib import admin
from .models import Watch, Category

# Регистрация модели в админке
@admin.register(Watch)
class WatchAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'category', 'is_published', 'created_at')
    list_filter = ('category', 'is_published')
    search_fields = ('title', 'description')
    list_editable = ('is_published',)
    list_per_page = 10

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

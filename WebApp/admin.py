from django.contrib import admin
from .models import Watch, Category

# Регистрация модели в админке
@admin.register(Watch)
class WatchAdmin(admin.ModelAdmin):
    list_display = ('title', 'category_id', 'price', 'status', 'created_at')
    list_filter = ('category_id', 'status')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

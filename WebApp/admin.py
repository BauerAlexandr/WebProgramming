from django.contrib import admin
from django.contrib import messages
from django.utils.safestring import mark_safe
from .models import Watch, Category, Tag, TechSpec

class ExpensiveFilter(admin.SimpleListFilter):
    title = 'Ценовой сегмент'
    parameter_name = 'price_segment'

    def lookups(self, request, model_admin):
        return [
            ('expensive', 'Дорогие (>500,000)'),
            ('affordable', 'Доступные (≤500,000)'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'expensive':
            return queryset.filter(price__gt=500000)
        elif self.value() == 'affordable':
            return queryset.filter(price__lte=500000)
        return queryset

@admin.register(Watch)
class WatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price', 'category', 'is_published', 'created_at', 'title_length', 'is_expensive', 'post_photo')
    list_display_links = ('id', 'title')
    list_editable = ('is_published', 'price')
    ordering = ['-created_at', 'title']
    list_per_page = 10
    actions = ['set_published', 'set_draft']
    search_fields = ['title__startswith', 'category__name']
    list_filter = [ExpensiveFilter, 'category__name', 'is_published']
    fields = ['title', 'slug', 'description', 'price', 'category', 'tags', 'tech_spec', 'is_published', 'image', 'post_photo']
    readonly_fields = ['post_photo']
    filter_horizontal = ['tags']

    @admin.display(description='Длина названия')
    def title_length(self, obj):
        return f"{len(obj.title)} символов"

    @admin.display(description='Дорогие часы')
    def is_expensive(self, obj):
        return obj.price > 500000
    is_expensive.boolean = True

    @admin.display(description='Изображение')
    def post_photo(self, watch):
        if watch.image:
            return mark_safe(f"<img src='{watch.image.url}' width=50>")
        return "Без фото"

    @admin.action(description='Опубликовать выбранные часы')
    def set_published(self, request, queryset):
        count = queryset.update(is_published=Watch.WatchStatus.PUBLISHED)
        self.message_user(request, f"Опубликовано {count} записи(ей).")

    @admin.action(description='Снять с публикации выбранные часы')
    def set_draft(self, request, queryset):
        count = queryset.update(is_published=Watch.WatchStatus.DRAFT)
        self.message_user(request, f"{count} записи(ей) сняты с публикации!", messages.WARNING)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')

@admin.register(TechSpec)
class TechSpecAdmin(admin.ModelAdmin):
    list_display = ('id', 'mechanism', 'water_resistance', 'case_material')
    list_display_links = ('id', 'mechanism')
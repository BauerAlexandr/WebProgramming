from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Поля, отображаемые в списке пользователей
    list_display = ('username', 'email', 'date_birth', 'is_staff', 'is_active')
    # Поля, по которым можно фильтровать
    list_filter = ('is_staff', 'is_active', 'groups')
    # Поля, по которым можно искать
    search_fields = ('username', 'email')
    # Поля для редактирования
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'date_birth', 'photo')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    # Поля для формы создания пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'date_birth', 'photo'),
        }),
    )
    # Поля, которые можно сортировать
    ordering = ('username',)
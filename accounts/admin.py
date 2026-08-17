from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """Administración del usuario personalizado con rol del dominio."""
    list_display = ('username', 'first_name', 'last_name', 'email', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'colegiatura')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Rol y perfil', {'fields': ('role', 'colegiatura', 'telefono')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Rol y perfil', {'fields': ('role', 'colegiatura', 'telefono')}),
    )

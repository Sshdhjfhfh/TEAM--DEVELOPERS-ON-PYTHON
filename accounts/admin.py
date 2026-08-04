from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Administración de perfiles en el sitio de administración."""
    list_display = ('user', 'role', 'colegiatura', 'telefono')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'colegiatura')


class ProfileInline(admin.StackedInline):
    """Muestra el perfil dentro del formulario del usuario."""
    model = Profile
    can_delete = False
    verbose_name_plural = 'Perfil'


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

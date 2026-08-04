from django.contrib import admin

from .models import Paciente


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('dni', 'nombres', 'apellidos', 'sexo', 'edad', 'telefono', 'activo', 'fecha_registro')
    list_filter = ('sexo', 'tipo_sangre', 'activo')
    search_fields = ('dni', 'nombres', 'apellidos', 'telefono')
    date_hierarchy = 'fecha_registro'
    readonly_fields = ('fecha_registro',)

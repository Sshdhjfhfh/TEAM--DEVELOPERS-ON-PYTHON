from django.contrib import admin

from .models import Cita, Estudiante


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = (
        'codigo',
        'nombre_completo',
        'escuela',
        'ciclo',
        'matriculado',
        'tiene_cuenta',
    )
    list_filter = ('escuela', 'matriculado')
    list_editable = ('matriculado',)
    search_fields = ('codigo', 'dni', 'nombres', 'apellidos')
    ordering = ('apellidos', 'nombres')


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'hora', 'estudiante', 'estado', 'creada_en')
    list_filter = ('estado', 'fecha')
    search_fields = (
        'estudiante__codigo',
        'estudiante__nombres',
        'estudiante__apellidos',
        'motivo',
    )
    autocomplete_fields = ('estudiante',)
    date_hierarchy = 'fecha'
    list_select_related = ('estudiante',)

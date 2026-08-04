from django.contrib import admin

from .models import Atencion, SignosVitales


class SignosVitalesInline(admin.StackedInline):
    model = SignosVitales
    extra = 0


@admin.register(Atencion)
class AtencionAdmin(admin.ModelAdmin):
    list_display = ('id', 'paciente', 'nivel_triage', 'estado', 'medico', 'fecha_atencion')
    list_filter = ('nivel_triage', 'estado', 'fecha_atencion')
    search_fields = ('paciente__dni', 'paciente__nombres', 'paciente__apellidos', 'motivo_consulta')
    date_hierarchy = 'fecha_atencion'
    inlines = (SignosVitalesInline,)


@admin.register(SignosVitales)
class SignosVitalesAdmin(admin.ModelAdmin):
    list_display = ('atencion', 'temperatura', 'presion_arterial', 'pulso', 'saturacion_oxigeno', 'registrado_en')

from django.contrib import admin

from .models import Medicamento, MovimientoInventario


@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'stock_actual', 'stock_minimo', 'unidad', 'precio_unitario', 'fecha_vencimiento')
    list_filter = ('categoria',)
    search_fields = ('nombre', 'proveedor')


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('medicamento', 'tipo', 'cantidad', 'usuario', 'fecha', 'motivo')
    list_filter = ('tipo', 'fecha')
    search_fields = ('medicamento__nombre', 'motivo')
    date_hierarchy = 'fecha'

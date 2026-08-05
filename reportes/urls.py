from django.urls import path

from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('pacientes/', views.reporte_pacientes, name='pacientes'),
    path('atenciones/', views.reporte_atenciones, name='atenciones'),
    path('inventario/', views.reporte_inventario, name='inventario'),
    path('pacientes/csv/', views.exportar_pacientes_csv, name='pacientes_csv'),
    path('atenciones/csv/', views.exportar_atenciones_csv, name='atenciones_csv'),
    path('inventario/csv/', views.exportar_inventario_csv, name='inventario_csv'),
    path('pacientes/imprimir/', views.imprimir_pacientes, name='pacientes_imprimir'),
    path('atenciones/imprimir/', views.imprimir_atenciones, name='atenciones_imprimir'),
    path('inventario/imprimir/', views.imprimir_inventario, name='inventario_imprimir'),
]

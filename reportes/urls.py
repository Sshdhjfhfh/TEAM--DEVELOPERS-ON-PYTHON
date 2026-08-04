from django.urls import path

from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('pacientes/', views.reporte_pacientes, name='pacientes'),
    path('atenciones/', views.reporte_atenciones, name='atenciones'),
    path('inventario/', views.reporte_inventario, name='inventario'),
]

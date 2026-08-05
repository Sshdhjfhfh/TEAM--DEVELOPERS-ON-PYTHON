from django.urls import path

from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.lista_medicamentos, name='lista'),
    path('nuevo/', views.crear_medicamento, name='crear'),
    path('<int:pk>/', views.detalle_medicamento, name='detalle'),
    path('<int:pk>/editar/', views.editar_medicamento, name='editar'),
    path('movimientos/', views.lista_movimientos, name='movimientos'),
    path('movimientos/nuevo/', views.registrar_movimiento, name='registrar_movimiento'),
]

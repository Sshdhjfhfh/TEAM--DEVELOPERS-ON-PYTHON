from django.urls import path

from . import views

app_name = 'pacientes'

urlpatterns = [
    path('', views.lista_pacientes, name='lista'),
    path('nuevo/', views.crear_paciente, name='crear'),
    path('<int:pk>/', views.detalle_paciente, name='detalle'),
    path('<int:pk>/editar/', views.editar_paciente, name='editar'),
    path('<int:pk>/retirar/', views.retirar_paciente, name='retirar'),
]

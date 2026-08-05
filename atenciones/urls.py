from django.urls import path

from . import views

app_name = 'atenciones'

urlpatterns = [
    path('', views.lista_atenciones, name='lista'),
    path('cola/', views.cola_atenciones, name='cola'),
    path('nueva/', views.crear_atencion, name='crear'),
    path('<int:pk>/', views.detalle_atencion, name='detalle'),
    path('<int:pk>/editar/', views.editar_atencion, name='editar'),
    path('<int:pk>/signos/', views.registrar_signos, name='signos'),
    path('<int:pk>/receta/', views.agregar_receta, name='agregar_receta'),
]

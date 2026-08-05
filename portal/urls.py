from django.urls import path

from . import views

app_name = 'portal'

urlpatterns = [
    path('', views.inicio_portal, name='inicio'),
    path('validar-codigo/', views.validar_codigo, name='validar_codigo'),
    path('completar-registro/', views.completar_registro, name='completar_registro'),
    path('mis-citas/', views.mis_citas, name='mis_citas'),
    path('reservar-cita/', views.reservar_cita, name='reservar_cita'),
    path('mis-citas/<int:pk>/cancelar/', views.cancelar_cita, name='cancelar_cita'),
    path('citas/', views.lista_citas, name='lista_citas'),
    path('citas/<int:pk>/atender/', views.convertir_cita, name='convertir_cita'),
]

from django.urls import include, path
from rest_framework.authtoken import views as authtoken_views
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api'

router = DefaultRouter()
router.register(r'usuarios', views.UsuarioViewSet, basename='usuario')
router.register(r'perfiles', views.ProfileViewSet, basename='perfil')
router.register(r'pacientes', views.PacienteViewSet, basename='paciente')
router.register(r'atenciones', views.AtencionViewSet, basename='atencion')
router.register(r'signos-vitales', views.SignosVitalesViewSet, basename='signos-vitales')
router.register(r'medicamentos', views.MedicamentoViewSet, basename='medicamento')
router.register(r'movimientos', views.MovimientoInventarioViewSet, basename='movimiento')
router.register(r'estudiantes', views.EstudianteViewSet, basename='estudiante')
router.register(r'citas', views.CitaViewSet, basename='cita')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', authtoken_views.obtain_auth_token, name='api-token'),
]

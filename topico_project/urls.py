from django.contrib import admin
from django.urls import include, path

from reportes import views as reportes_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', reportes_views.dashboard, name='dashboard'),
    path('cuentas/', include('accounts.urls')),
    path('pacientes/', include('pacientes.urls')),
    path('atenciones/', include('atenciones.urls')),
    path('inventario/', include('inventario.urls')),
    path('reportes/', include('reportes.urls')),
    path('portal/', include('portal.urls')),
    path('api/', include('api.urls')),
]

"""Decoradores de autorización por rol para el Tópico UNH."""

from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .models import Profile

# Roles con permiso de gestión por módulo
ROLES_GESTION_PACIENTES = ('ADMIN', 'MEDICO', 'ENFERMERO')
ROLES_GESTION_ATENCIONES = ('ADMIN', 'MEDICO', 'ENFERMERO')
ROLES_GESTION_INVENTARIO = ('ADMIN', 'FARMACEUTICO')
ROLES_AGENDA_CITAS = ('ADMIN', 'MEDICO', 'ENFERMERO')


def rol_requerido(*roles):
    """Permite ejecutar la vista solo a los roles indicados.

    Los superusuarios siempre tienen acceso. Un estudiante es redirigido a su
    portal; el resto de roles no autorizados recibe un mensaje y se le envía
    al dashboard.
    """

    def decorador(vista):
        @wraps(vista)
        def envoltura(request, *args, **kwargs):
            perfil = getattr(request.user, 'profile', None)
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.is_superuser or (perfil is not None and perfil.role in roles):
                return vista(request, *args, **kwargs)
            if perfil is not None and perfil.role == Profile.Role.ESTUDIANTE:
                return redirect('portal:mis_citas')
            messages.error(request, 'No tiene permiso para realizar esta acción.')
            return redirect('dashboard')

        return envoltura

    return decorador

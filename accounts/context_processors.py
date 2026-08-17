def permisos_roles(request):
    """Expone permisos por rol a todas las plantillas.

    Se usa para ocultar/mostrar acciones de escritura según el rol del
    usuario, evitando duplicar la lógica en cada vista.
    """
    puede_clinico = False
    puede_inventario = False
    if request.user.is_authenticated:
        rol = getattr(request.user, 'role', None)
        puede_clinico = rol in ('ADMIN', 'MEDICO', 'ENFERMERO')
        puede_inventario = rol in ('ADMIN', 'FARMACEUTICO')
    return {
        'puede_clinico': puede_clinico,
        'puede_inventario': puede_inventario,
        'es_estudiante': request.user.is_authenticated and getattr(request.user, 'role', None) == 'ESTUDIANTE',
    }

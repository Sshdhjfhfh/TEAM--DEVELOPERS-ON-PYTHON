from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.decorators import ROLES_GESTION_PACIENTES, rol_requerido

from .models import Paciente


def _crear_paciente_desde_post(request):
    """Crea o actualiza un Paciente desde los datos crudos del POST."""
    datos = {
        'nombres': request.POST.get('nombres', '').strip(),
        'apellidos': request.POST.get('apellidos', '').strip(),
        'dni': request.POST.get('dni', '').strip(),
        'sexo': request.POST.get('sexo', ''),
        'telefono': request.POST.get('telefono', '').strip(),
        'direccion': request.POST.get('direccion', '').strip(),
        'tipo_sangre': request.POST.get('tipo_sangre', ''),
        'alergias': request.POST.get('alergias', '').strip(),
    }
    fecha_nacimiento = request.POST.get('fecha_nacimiento', '')
    if fecha_nacimiento:
        datos['fecha_nacimiento'] = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
    else:
        datos['fecha_nacimiento'] = None
    return datos


def _error_para_mensaje(exc):
    """Convierte un ValidationError en un mensaje legible."""
    if hasattr(exc, 'message_dict'):
        return '; '.join(
            f'{campo}: {" ".join(errs)}' for campo, errs in exc.message_dict.items()
        )
    return '; '.join(str(e) for e in exc.messages)


@login_required
def lista_pacientes(request):
    """Lista de pacientes con búsqueda por nombre o DNI y filtro de estado."""
    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', 'activos')
    pacientes = Paciente.objects.all()
    if estado == 'inactivos':
        pacientes = pacientes.filter(activo=False)
    else:
        pacientes = pacientes.filter(activo=True)
    if q:
        pacientes = pacientes.filter(
            dni__icontains=q,
        ) | pacientes.filter(
            nombres__icontains=q,
        ) | pacientes.filter(
            apellidos__icontains=q,
        )
    return render(
        request,
        'pacientes/lista.html',
        {'pacientes': pacientes.distinct(), 'q': q, 'estado': estado},
    )


@login_required
def detalle_paciente(request, pk):
    """Detalle de un paciente con su historial de atenciones."""
    paciente = get_object_or_404(Paciente, pk=pk)
    atenciones = paciente.atenciones.all().select_related('medico')
    return render(
        request,
        'pacientes/detalle.html',
        {'paciente': paciente, 'atenciones': atenciones},
    )


@login_required
@rol_requerido(*ROLES_GESTION_PACIENTES)
@require_http_methods(['GET', 'POST'])
def crear_paciente(request):
    """Registro de un nuevo paciente."""
    errores = None
    if request.method == 'POST':
        datos = _crear_paciente_desde_post(request)
        try:
            paciente = Paciente(**datos)
            paciente.registrado_por = request.user
            paciente.save()
            messages.success(request, f'Paciente {paciente.nombre_completo} registrado.')
            return redirect('pacientes:detalle', pk=paciente.pk)
        except ValidationError as exc:
            errores = _error_para_mensaje(exc)
    return render(request, 'pacientes/form.html', {
        'titulo': 'Registrar paciente',
        'datos': request.POST if request.method == 'POST' else None,
        'errores': errores,
        'sexos': Paciente.Sexo.choices,
        'tipos_sangre': Paciente.TipoSangre.choices,
    })


@login_required
@rol_requerido(*ROLES_GESTION_PACIENTES)
@require_http_methods(['GET', 'POST'])
def editar_paciente(request, pk):
    """Edición de un paciente existente."""
    paciente = get_object_or_404(Paciente, pk=pk)
    errores = None
    if request.method == 'POST':
        datos = _crear_paciente_desde_post(request)
        for campo, valor in datos.items():
            setattr(paciente, campo, valor)
        try:
            paciente.save()
            messages.success(request, f'Paciente {paciente.nombre_completo} actualizado.')
            return redirect('pacientes:detalle', pk=paciente.pk)
        except ValidationError as exc:
            errores = _error_para_mensaje(exc)
    return render(request, 'pacientes/form.html', {
        'titulo': 'Editar paciente',
        'paciente': paciente,
        'datos': request.POST if request.method == 'POST' else None,
        'errores': errores,
        'sexos': Paciente.Sexo.choices,
        'tipos_sangre': Paciente.TipoSangre.choices,
    })


@login_required
@rol_requerido(*ROLES_GESTION_PACIENTES)
@require_http_methods(['POST'])
def retirar_paciente(request, pk):
    """Retiro lógico de un paciente: cambia su estado, nunca lo elimina."""
    paciente = get_object_or_404(Paciente, pk=pk)
    paciente.activo = not paciente.activo
    paciente.save(update_fields=['activo'])
    if paciente.activo:
        messages.success(request, f'Paciente {paciente.nombre_completo} reactivado.')
    else:
        messages.success(request, f'Paciente {paciente.nombre_completo} dado de baja.')
    return redirect('pacientes:detalle', pk=paciente.pk)

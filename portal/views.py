"""Vistas del portal de estudiantes del Tópico UNH.

Incluye el registro en dos pasos (validación del código de matrícula y
completado de datos), el panel del estudiante, la reserva de citas y la
agenda del personal de salud.
"""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from atenciones.models import Atencion

from .forms import CitaForm, CompletarRegistroForm, ValidarCodigoForm
from .models import Cita, Estudiante

SESION_ESTUDIANTE = 'portal_estudiante_id'


def _perfil(usuario):
    return getattr(usuario, 'profile', None)


def _estudiante_de_usuario(usuario):
    return getattr(usuario, 'estudiante', None)


def _es_estudiante(usuario):
    perfil = _perfil(usuario)
    return (
        usuario.is_authenticated
        and perfil is not None
        and perfil.es_estudiante
        and _estudiante_de_usuario(usuario) is not None
    )


def inicio_portal(request):
    """Punto de entrada del portal: panel del estudiante o agenda del personal."""
    if not request.user.is_authenticated:
        return redirect('portal:validar_codigo')
    if _es_estudiante(request.user):
        estudiante = _estudiante_de_usuario(request.user)
        return render(
            request,
            'portal/inicio.html',
            {
                'estudiante': estudiante,
                'proximas_citas': estudiante.citas.filter(
                    estado__in=[Cita.Estado.PENDIENTE, Cita.Estado.CONFIRMADA],
                ).order_by('fecha', 'hora'),
                'historial_citas': estudiante.citas.count(),
            },
        )
    return redirect('portal:lista_citas')


# ---------------------------------------------------------------------------
# Registro del estudiante (dos pasos)
# ---------------------------------------------------------------------------
def validar_codigo(request):
    """Paso 1 del registro: verificar código de matrícula y DNI en el padrón."""
    if request.user.is_authenticated:
        return redirect('portal:inicio')
    form = ValidarCodigoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        request.session[SESION_ESTUDIANTE] = form.cleaned_data['estudiante'].pk
        return redirect('portal:completar_registro')
    return render(request, 'portal/validar_codigo.html', {'form': form})


def completar_registro(request):
    """Paso 2 del registro: datos complementarios y contraseña."""
    if request.user.is_authenticated:
        return redirect('portal:inicio')
    estudiante_id = request.session.get(SESION_ESTUDIANTE)
    if not estudiante_id:
        return redirect('portal:validar_codigo')
    estudiante = get_object_or_404(Estudiante, pk=estudiante_id)
    if estudiante.tiene_cuenta or not estudiante.matriculado:
        request.session.pop(SESION_ESTUDIANTE, None)
        messages.error(request, 'El código ya no es válido para completar el registro.')
        return redirect('portal:validar_codigo')

    form = CompletarRegistroForm(request.POST or None, estudiante=estudiante)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        request.session.pop(SESION_ESTUDIANTE, None)
        messages.success(
            request,
            f'Bienvenido/a, {estudiante.nombres}. Su cuenta se creó correctamente.',
        )
        return redirect('portal:inicio')
    return render(
        request,
        'portal/completar_registro.html',
        {'form': form, 'estudiante': estudiante},
    )


# ---------------------------------------------------------------------------
# Panel del estudiante
# ---------------------------------------------------------------------------
@login_required
def mis_citas(request):
    """Citas del estudiante autenticado."""
    estudiante = _estudiante_de_usuario(request.user)
    if estudiante is None:
        return redirect('portal:inicio')
    citas = estudiante.citas.select_related('atencion').order_by('-fecha', '-hora')
    return render(request, 'portal/mis_citas.html', {'citas': citas})


@login_required
@require_http_methods(['GET', 'POST'])
def reservar_cita(request):
    """Reserva de una cita de atención en el Tópico."""
    estudiante = _estudiante_de_usuario(request.user)
    if estudiante is None:
        return redirect('portal:inicio')
    fecha = request.GET.get('fecha')
    form = CitaForm(
        request.POST or None,
        estudiante=estudiante,
        initial={'fecha': fecha} if fecha else None,
    )
    if request.method == 'POST' and form.is_valid():
        cita = form.save(commit=False)
        cita.estudiante = estudiante
        cita.save()
        messages.success(
            request,
            'Cita reservada para el '
            f'{cita.fecha:%d/%m/%Y} a las {cita.hora:%H:%M}. '
            'Preséntese al Tópico a la hora indicada.',
        )
        return redirect('portal:mis_citas')
    return render(request, 'portal/reservar_cita.html', {'form': form})


@login_required
@require_http_methods(['POST'])
def cancelar_cita(request, pk):
    """Cancelación de una cita propia (solo pendiente o confirmada)."""
    estudiante = _estudiante_de_usuario(request.user)
    if estudiante is None:
        return redirect('portal:inicio')
    cita = get_object_or_404(Cita, pk=pk, estudiante=estudiante)
    if cita.activa:
        cita.estado = Cita.Estado.CANCELADA
        cita.save(update_fields=['estado'])
        messages.success(request, 'Su cita fue cancelada correctamente.')
    else:
        messages.warning(request, 'La cita seleccionada ya no puede cancelarse.')
    return redirect('portal:mis_citas')


# ---------------------------------------------------------------------------
# Agenda del personal de salud
# ---------------------------------------------------------------------------
@login_required
def lista_citas(request):
    """Agenda de citas del Tópico con filtros (personal de salud)."""
    if _es_estudiante(request.user):
        return redirect('portal:mis_citas')
    citas = Cita.objects.select_related(
        'estudiante__paciente',
        'atencion',
    ).all()
    estado = request.GET.get('estado', '')
    fecha = request.GET.get('fecha', '')
    q = request.GET.get('q', '').strip()

    if estado:
        citas = citas.filter(estado=estado)
    if fecha:
        citas = citas.filter(fecha=fecha)
    if q:
        citas = citas.filter(
            estudiante__codigo__icontains=q,
        ) | citas.filter(
            estudiante__nombres__icontains=q,
        ) | citas.filter(
            estudiante__apellidos__icontains=q,
        )

    return render(
        request,
        'portal/citas.html',
        {
            'citas': citas.distinct(),
            'estado': estado,
            'fecha': fecha,
            'q': q,
            'estado_opciones': Cita.Estado.choices,
            'pendientes': Cita.objects.filter(estado=Cita.Estado.PENDIENTE).count(),
            'confirmadas': Cita.objects.filter(estado=Cita.Estado.CONFIRMADA).count(),
        },
    )


@login_required
@require_http_methods(['GET', 'POST'])
def convertir_cita(request, pk):
    """Convierte una cita vigente en una atención médica (personal de salud)."""
    if _es_estudiante(request.user):
        return redirect('portal:mis_citas')
    cita = get_object_or_404(
        Cita.objects.select_related('estudiante__paciente'),
        pk=pk,
    )
    if not cita.activa:
        messages.warning(request, 'La cita seleccionada no se encuentra vigente.')
        return redirect('portal:lista_citas')

    if request.method == 'POST':
        paciente = cita.estudiante.paciente
        if paciente is None:
            messages.error(request, 'El estudiante no tiene una ficha de paciente vinculada.')
            return redirect('portal:lista_citas')
        atencion = Atencion.objects.create(
            paciente=paciente,
            medico=request.user,
            motivo_consulta=cita.motivo,
        )
        cita.atencion = atencion
        cita.estado = Cita.Estado.ATENDIDA
        cita.save(update_fields=['atencion', 'estado'])
        messages.success(
            request,
            f'Cita de {cita.estudiante.nombre_completo} convertida en la atención #{atencion.pk}.',
        )
        return redirect('atenciones:detalle', pk=atencion.pk)
    return render(request, 'portal/convertir_cita.html', {'cita': cita})

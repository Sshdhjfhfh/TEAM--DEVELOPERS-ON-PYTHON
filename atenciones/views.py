from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.decorators import ROLES_GESTION_ATENCIONES, rol_requerido
from inventario.models import Medicamento
from pacientes.models import Paciente

from .models import Atencion, SignosVitales


def _error_para_mensaje(exc):
    """Convierte un ValidationError en un mensaje legible."""
    if hasattr(exc, 'message_dict'):
        return '; '.join(
            f'{campo}: {" ".join(errs)}' for campo, errs in exc.message_dict.items()
        )
    return '; '.join(str(e) for e in exc.messages)


def _entero_o_nulo(valor):
    valor = (valor or '').strip()
    return int(valor) if valor else None


def _decimal_o_nulo(valor):
    valor = (valor or '').strip()
    return float(valor) if valor else None


def _atencion_desde_post(request):
    """Convierte el POST en los datos de una Atención."""
    return {
        'paciente': get_object_or_404(Paciente, pk=request.POST.get('paciente')),
        'medico_id': _entero_o_nulo(request.POST.get('medico')),
        'motivo_consulta': request.POST.get('motivo_consulta', '').strip(),
        'anamnesis': request.POST.get('anamnesis', '').strip(),
        'diagnostico': request.POST.get('diagnostico', '').strip(),
        'tratamiento': request.POST.get('tratamiento', '').strip(),
        'observaciones': request.POST.get('observaciones', '').strip(),
        'nivel_triage': request.POST.get('nivel_triage', Atencion.NivelTriage.AMARILLO),
        'estado': request.POST.get('estado', Atencion.Estado.EN_ESPERA),
    }


@login_required
def lista_atenciones(request):
    """Lista de atenciones con filtros por estado, triage y búsqueda."""
    atenciones = Atencion.objects.select_related('paciente', 'medico').all()
    estado = request.GET.get('estado', '')
    triage = request.GET.get('triage', '')
    q = request.GET.get('q', '').strip()

    if estado:
        atenciones = atenciones.filter(estado=estado)
    if triage:
        atenciones = atenciones.filter(nivel_triage=triage)
    if q:
        atenciones = atenciones.filter(
            paciente__dni__icontains=q,
        ) | atenciones.filter(
            paciente__nombres__icontains=q,
        ) | atenciones.filter(
            paciente__apellidos__icontains=q,
        )

    return render(
        request,
        'atenciones/lista.html',
        {
            'atenciones': atenciones.distinct(),
            'estado': estado,
            'triage': triage,
            'q': q,
        },
    )


@login_required
def detalle_atencion(request, pk):
    """Detalle de una atención con sus signos vitales y receta."""
    atencion = get_object_or_404(
        Atencion.objects.select_related('paciente', 'medico'),
        pk=pk,
    )
    signos = getattr(atencion, 'signos_vitales', None)
    receta = atencion.receta.select_related('medicamento').all()
    return render(
        request,
        'atenciones/detalle.html',
        {
            'atencion': atencion,
            'signos': signos,
            'receta': receta,
            'medicamentos': Medicamento.objects.all(),
        },
    )


@login_required
@rol_requerido(*ROLES_GESTION_ATENCIONES)
@require_http_methods(['GET', 'POST'])
def crear_atencion(request):
    """Registra una nueva atención médica."""
    errores = None
    if request.method == 'POST':
        try:
            atencion = Atencion(**_atencion_desde_post(request))
            atencion.save()
            messages.success(
                request,
                f'Atención #{atencion.pk} registrada para {atencion.paciente.nombre_completo}.',
            )
            return redirect('atenciones:detalle', pk=atencion.pk)
        except (ValueError, ValidationError) as exc:
            errores = _error_para_mensaje(exc) if isinstance(exc, ValidationError) else str(exc)
    return render(
        request,
        'atenciones/form.html',
        {
            'titulo': 'Nueva atención',
            'pacientes': Paciente.objects.filter(activo=True),
            'medicos': _medicos_atencion(),
            'niveles': Atencion.NivelTriage.choices,
            'estados': Atencion.Estado.choices,
            'datos': request.POST if request.method == 'POST' else None,
            'errores': errores,
        },
    )


@login_required
@rol_requerido(*ROLES_GESTION_ATENCIONES)
@require_http_methods(['GET', 'POST'])
def editar_atencion(request, pk):
    """Edita una atención médica existente."""
    atencion = get_object_or_404(Atencion, pk=pk)
    errores = None
    if request.method == 'POST':
        try:
            datos = _atencion_desde_post(request)
            for campo, valor in datos.items():
                setattr(atencion, campo, valor)
            atencion.save()
            messages.success(request, f'Atención #{atencion.pk} actualizada.')
            return redirect('atenciones:detalle', pk=atencion.pk)
        except (ValueError, ValidationError) as exc:
            errores = _error_para_mensaje(exc) if isinstance(exc, ValidationError) else str(exc)
    return render(
        request,
        'atenciones/form.html',
        {
            'titulo': f'Editar atención #{atencion.pk}',
            'atencion': atencion,
            'pacientes': Paciente.objects.filter(activo=True),
            'medicos': _medicos_atencion(),
            'niveles': Atencion.NivelTriage.choices,
            'estados': Atencion.Estado.choices,
            'datos': request.POST if request.method == 'POST' else None,
            'errores': errores,
        },
    )


def _medicos_atencion():
    """Personal de salud (médicos, enfermeros y farmacéuticos) para el desplegable."""
    from accounts.models import CustomUser
    return CustomUser.objects.filter(
        role__in=['MEDICO', 'ENFERMERO', 'FARMACEUTICO'],
    ).order_by('first_name', 'last_name')


@login_required
@rol_requerido(*ROLES_GESTION_ATENCIONES)
@require_http_methods(['GET', 'POST'])
def registrar_signos(request, pk):
    """Registra o actualiza los signos vitales de una atención."""
    atencion = get_object_or_404(Atencion, pk=pk)
    signos, _ = SignosVitales.objects.get_or_create(atencion=atencion)
    errores = None
    if request.method == 'POST':
        campos = (
            'temperatura',
            'presion_sistolica',
            'presion_diastolica',
            'pulso',
            'frecuencia_respiratoria',
            'saturacion_oxigeno',
            'peso',
            'talla',
        )
        for campo in campos:
            if campo in ('temperatura', 'peso', 'talla'):
                valor = _decimal_o_nulo(request.POST.get(campo))
            else:
                valor = _entero_o_nulo(request.POST.get(campo))
            setattr(signos, campo, valor)
        try:
            signos.save()
            messages.success(request, f'Signos vitales de la atención #{pk} registrados.')
            return redirect('atenciones:detalle', pk=pk)
        except (ValueError, ValidationError) as exc:
            errores = _error_para_mensaje(exc) if isinstance(exc, ValidationError) else str(exc)
    return render(
        request,
        'atenciones/signos.html',
        {'atencion': atencion, 'signos': signos, 'errores': errores},
    )


@login_required
@rol_requerido(*ROLES_GESTION_ATENCIONES)
@require_http_methods(['POST'])
def agregar_receta(request, pk):
    """Agrega un medicamento a la receta de una atención (descuenta stock)."""
    atencion = get_object_or_404(Atencion, pk=pk)
    from .models import RecetaMedicamento
    try:
        item = RecetaMedicamento(
            atencion=atencion,
            medicamento=get_object_or_404(Medicamento, pk=request.POST.get('medicamento')),
            cantidad=int(request.POST.get('cantidad') or 0),
            indicaciones=request.POST.get('indicaciones', '').strip(),
        )
        item.save()
        messages.success(
            request,
            f'{item.cantidad} {item.medicamento.unidad} de {item.medicamento.nombre} '
            'agregados a la receta.',
        )
    except (ValueError, ValidationError) as exc:
        if isinstance(exc, ValidationError) and hasattr(exc, 'message_dict'):
            mensajes = []
            for errs in exc.message_dict.values():
                mensajes.extend(errs)
        else:
            mensajes = exc.messages if isinstance(exc, ValidationError) else [str(exc)]
        for error in mensajes:
            messages.error(request, error)
    return redirect('atenciones:detalle', pk=pk)


@login_required
@rol_requerido(*ROLES_GESTION_ATENCIONES)
def cola_atenciones(request):
    """Cola de pacientes por triage: en espera y en atención (emergencias primero)."""
    atenciones = (
        Atencion.objects.select_related('paciente')
        .filter(estado__in=[Atencion.Estado.EN_ESPERA, Atencion.Estado.EN_ATENCION])
    )
    orden_triage = {
        Atencion.NivelTriage.ROJO: 0,
        Atencion.NivelTriage.NARANJA: 1,
        Atencion.NivelTriage.AMARILLO: 2,
        Atencion.NivelTriage.VERDE: 3,
        Atencion.NivelTriage.AZUL: 4,
    }
    atenciones = sorted(atenciones, key=lambda a: (orden_triage[a.nivel_triage], a.fecha_atencion))
    conteo = {}
    for nivel in Atencion.NivelTriage.choices:
        conteo[nivel[0]] = Atencion.objects.filter(
            nivel_triage=nivel[0],
            estado=Atencion.Estado.EN_ESPERA,
        ).count()
    return render(request, 'atenciones/cola.html', {'atenciones': atenciones, 'conteo': conteo})

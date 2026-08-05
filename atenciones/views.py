from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.decorators import ROLES_GESTION_ATENCIONES, rol_requerido
from pacientes.models import Paciente

from .forms import AtencionForm, RecetaForm, SignosVitalesForm
from .models import Atencion, SignosVitales


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
            'receta_form': RecetaForm(),
        },
    )


@login_required
@rol_requerido(*ROLES_GESTION_ATENCIONES)
@require_http_methods(['GET', 'POST'])
def crear_atencion(request):
    """Registra una nueva atención médica."""
    form = AtencionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        atencion = form.save()
        messages.success(request, f'Atención #{atencion.pk} registrada para {atencion.paciente.nombre_completo}.')
        return redirect('atenciones:detalle', pk=atencion.pk)
    return render(request, 'atenciones/form.html', {'form': form, 'titulo': 'Nueva atención'})


@login_required
@rol_requerido(*ROLES_GESTION_ATENCIONES)
@require_http_methods(['GET', 'POST'])
def editar_atencion(request, pk):
    """Edita una atención médica existente."""
    atencion = get_object_or_404(Atencion, pk=pk)
    form = AtencionForm(request.POST or None, instance=atencion)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Atención #{atencion.pk} actualizada.')
        return redirect('atenciones:detalle', pk=atencion.pk)
    return render(request, 'atenciones/form.html', {'form': form, 'titulo': f'Editar atención #{atencion.pk}', 'atencion': atencion})


@login_required
@rol_requerido(*ROLES_GESTION_ATENCIONES)
@require_http_methods(['GET', 'POST'])
def registrar_signos(request, pk):
    """Registra o actualiza los signos vitales de una atención."""
    atencion = get_object_or_404(Atencion, pk=pk)
    signos, _ = SignosVitales.objects.get_or_create(atencion=atencion)
    form = SignosVitalesForm(request.POST or None, instance=signos)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Signos vitales de la atención #{pk} registrados.')
        return redirect('atenciones:detalle', pk=pk)
    return render(request, 'atenciones/signos.html', {'form': form, 'atencion': atencion, 'signos': signos})


@login_required
@rol_requerido(*ROLES_GESTION_ATENCIONES)
@require_http_methods(['POST'])
def agregar_receta(request, pk):
    """Agrega un medicamento a la receta de una atención (descuenta stock)."""
    atencion = get_object_or_404(Atencion, pk=pk)
    form = RecetaForm(request.POST)
    if form.is_valid():
        item = form.save(commit=False)
        item.atencion = atencion
        item.save()
        messages.success(
            request,
            f'{item.cantidad} {item.medicamento.unidad} de {item.medicamento.nombre} '
            'agregados a la receta.',
        )
    else:
        for errores in form.errors.values():
            for error in errores:
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

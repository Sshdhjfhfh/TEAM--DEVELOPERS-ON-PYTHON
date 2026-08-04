from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import PacienteForm
from .models import Paciente


@login_required
def lista_pacientes(request):
    """Lista de pacientes con búsqueda por nombre o DNI."""
    q = request.GET.get('q', '').strip()
    pacientes = Paciente.objects.all()
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
        {'pacientes': pacientes.distinct(), 'q': q},
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
@require_http_methods(['GET', 'POST'])
def crear_paciente(request):
    """Registro de un nuevo paciente."""
    form = PacienteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        paciente = form.save(commit=False)
        paciente.registrado_por = request.user
        paciente.save()
        messages.success(request, f'Paciente {paciente.nombre_completo} registrado.')
        return redirect('pacientes:detalle', pk=paciente.pk)
    return render(request, 'pacientes/form.html', {'form': form, 'titulo': 'Registrar paciente'})


@login_required
@require_http_methods(['GET', 'POST'])
def editar_paciente(request, pk):
    """Edición de un paciente existente."""
    paciente = get_object_or_404(Paciente, pk=pk)
    form = PacienteForm(request.POST or None, instance=paciente)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Paciente {paciente.nombre_completo} actualizado.')
        return redirect('pacientes:detalle', pk=paciente.pk)
    return render(request, 'pacientes/form.html', {'form': form, 'titulo': 'Editar paciente', 'paciente': paciente})
